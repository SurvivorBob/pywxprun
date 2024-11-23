from __future__ import annotations

import models.prun as prun
import logging

import pubsub.pub
import json

from models.util import dict_add, dict_mul

import math
import re
import copy
import time

import traceback

infrastructureBuildingTickers = ['HB1', 'HB2', 'HB3', 'HB4', 'HB5', 'HBB', 'HBC', 'HBM', 'HBL', 'STO']
expertTypes = [
    "AGRICULTURE",
    "CHEMISTRY",
    "CONSTRUCTION",
    "ELECTRONICS",
    "FOOD_INDUSTRIES",
    "FUEL_REFINING",
    "MANUFACTURING",
    "METALLURGY",
    "RESOURCE_EXTRACTION"
]
expertMultiplierPerCount = [1, 1.0306, 1.0696, 1.1248, 1.1974, 1.2840]
shipCapacities = [
    (500, 500),
    (3000, 1000),
    (2000, 2000),
    (1000, 3000)
]

workerTypeOrdering = ["Pioneers", "Settlers", "Technicians", "Engineers", "Scientists"]

cogmIgnores = ["NA"]

from models.util import dict_add, dict_mul

MS_PER_DAY = 86400 * 1000

DEFAULT_TARGET_D = 14

class Empire:
    def __init__(self):
        self.bases: list[Base] = []
        self.permits = 2

        self.companyHQ: prun.Planet = None

        self.basesMap : dict[str, Base] = {}

    def serialize(self):
        out = {}
        out['permits'] = self.permits
        out['bases'] = [b.serialize() for b in self.bases]

        return out

    @classmethod
    def unserialize(cls, inp):
        out = cls()
        out.permits = inp['permits']
        out.bases = [Base.unserialize(out, b) for b in inp['bases']]

        out.basesMap = {b.planet.PlanetNaturalId: b for b in out.bases}

        return out

    @classmethod
    def loadFromFIO(cls):
        if not prun.fio_api_key:
            logging.warn("Empire.loadFromFIO: no API key defined in pywxprun.cfg!")
            return None
        un = prun.config['Config']['UserName']
        if not un:
            logging.warn("Empire.loadFromFIO: no username defined in pywxprun.cfg!")
            return None

        out = cls()
        sites = prun.fio_get(f"/sites/{un}")

        base_map : dict[str, Base] = {}

        for site in sites:
            bs = Base(out, prun.planets[site['PlanetIdentifier']])
            bs.SiteId = site['SiteId']

            repairInterval = bs.getSuggestedRepairIntervalDays()
            buis = {}
            for bui in site['Buildings']:
                bui_ticker = bui['BuildingTicker']
                if bui_ticker in buis:
                    buis[bui_ticker] += 1
                else:
                    buis[bui_ticker] = 1
                if prun.buildings[bui_ticker].Expertise and (bui['BuildingLastRepair'] or bui['BuildingCreated']) < (time.time() - repairInterval * 86400) * 1000:
                    print(bui_ticker)
                    bs._needsRepair = True
            for bui_ticker, n in buis.items():
                bs.setBuildingCount(bui_ticker, n)

            out.bases.append(bs)
            base_map[site['PlanetIdentifier']] = bs

        # logging.info([k for k in base_map.keys()])

        lines = prun.fio_get(f"/production/{un}")

        for line in lines:
            if line['PlanetNaturalId'] not in base_map:
                logging.warn(f"Empire#loadFromFIO: no site for {line['PlanetNaturalId']}, open BS in a buffer and restart planner")
                continue
            bs = base_map[line['PlanetNaturalId']]
            bui = prun.buildings[line['Type']]
            recipeCounts = {}
            for o in line['Orders']:
                if o['Recurring'] and o['CompletedPercentage'] is None:
                    recipeKey = o['StandardRecipeName']
                    validRecipeKeys = bs.recipeIdsForBuilding(bui.Ticker)
                    if bui.Ticker in ["EXT", "COL", "RIG"]:
                        outMatTicker = o['Outputs'][0]['MaterialTicker']
                        recipeKey = [k for k in validRecipeKeys if outMatTicker in k][0]
                        recipe = prun.recipes[recipeKey]

                        output0 = o['Outputs'][0]
                        output0ticker, output0qty = output0['MaterialTicker'], output0['MaterialAmount']
                        runQty = recipe.Outputs[output0ticker]
                        numRuns = round(output0qty / runQty)
                    else:
                        orderInputs = {x['MaterialTicker']: x['MaterialAmount'] for x in o['Inputs']}
                        orderOutputs = {x['MaterialTicker']: x['MaterialAmount'] for x in o['Outputs']}
                        for rk in validRecipeKeys:
                            recipe = prun.recipes[rk]
                            if set(orderInputs.keys()) == set(recipe.Inputs.keys()) and set(orderOutputs.keys()) == set(recipe.Outputs.keys()):
                                out0_ticker = o['Outputs'][0]['MaterialTicker']
                                testRuns = orderOutputs[out0_ticker] // recipe.Outputs[out0_ticker]
                                testInputs = dict_mul(recipe.Inputs, testRuns)
                                testOutputs = dict_mul(recipe.Outputs, testRuns)
                                match = True
                                for k, v in testInputs.items():
                                    if orderInputs[k] != v:
                                        match = False
                                        break
                                for k, v in testOutputs.items():
                                    if orderOutputs[k] != v:
                                        match = False
                                        break
                                if match:
                                    recipeKey = rk
                                    numRuns = testRuns
                                    break


                    recipeCounts[recipeKey] = recipeCounts.get(recipeKey, 0) + numRuns

            for recipeKey, count in recipeCounts.items():
                bs.setRecipeQty(recipeKey, count)

        out.basesMap = base_map
        return out

    def announceChanges(self):
        pubsub.pub.sendMessage("empire_changed", empire_id=id(self))


    def getTotalMaterialFlow(self):
        ret = {}
        for b in self.bases:
            ret = dict_add(ret, b.getDailyMaterialFlow())

        return ret

    def createBase(self, planet_id):
        if planet_id in prun.planets:
            b = Base(self, prun.planets[planet_id])
            self.bases.append(b)

            self.basesMap = {b.planet.PlanetNaturalId: b for b in self.bases}

            self.announceChanges()
            return b
        else:
            return None

    def deleteBase(self, base):
        if base in self.bases:
            self.bases.remove(base)
            self.announceChanges()

    def getProfitForSingleMaterialFlow(self, ticker, qty):
        mat = prun.materials[ticker]
        if qty > 0:
            return mat.getSellCostForQtyInMarket(qty)
        else:
            return mat.getBuyCostForQtyInMarket(qty)

    def getBaseForPlanet(self, planet_id):
        return self.basesMap.get(planet_id, None)

    def getCompanyHQBonuses(self):
        if self.companyHQ == None:
            return {}
        faction = self.companyHQ.FactionCode
        return {
            "IC": {
                "AGRICULTURE": 1.06,
                "FOOD_INDUSTRIES": 1.04,
            },
            "NC": {
                "METALLURGY": 1.04,
                "CONSTRUCTION": 1.06,
            },
            "AI": {
                "ELECTRONICS": 1.1,
            },
            "CI": {
                "MANUFACTURING": 1.1,
            },
            None: {
                "CHEMISTRY": 1.04,
                "FUEL_REFINING": 1.04,
                "RESOURCE_EXTRACTION": 1.04,
            }
        }[faction]

    def getMaterialFlowsByHub(self):
        ret = {}

        for b in self.bases:
            sf_key = b.supplyFrom
            if not sf_key:
                continue
            if sf_key not in prun.storages:
                continue

            if sf_key not in ret:
                ret[sf_key] = {}

            ret[sf_key] = dict_add(ret[sf_key], b.getDailyMaterialFlow(True))

        return ret

    def getMaterialInFlowsByHub(self):
        ret = {}

        for b in self.bases:
            sf_key = b.supplyFrom
            if not sf_key:
                continue
            if sf_key not in prun.storages:
                continue

            if sf_key not in ret:
                ret[sf_key] = {}

            ret[sf_key] = dict_add(ret[sf_key], {k: v for k, v in b.getDailyMaterialFlow(True).items() if v < 0})

        return ret

    def getMaterialOutFlowsByHub(self):
        ret = {}

        for b in self.bases:
            sf_key = b.supplyFrom
            if not sf_key:
                continue
            if sf_key not in prun.storages:
                continue

            if sf_key not in ret:
                ret[sf_key] = {}

            ret[sf_key] = dict_add(ret[sf_key], {k: v for k, v in b.getDailyMaterialFlow(True).items() if v > 0})

        return ret

    def getMaterialPendingByHub(self):
        ret = {}

        for b in self.bases:
            sf_key = b.supplyFrom
            if not sf_key:
                continue
            if sf_key not in prun.storages:
                continue

            if sf_key not in ret:
                ret[sf_key] = {}

            ret[sf_key] = dict_add(ret[sf_key], b.getSupplyListAndDuration(float('inf'), float('inf'))[0])

        return ret

    def getInventorySurplusesByHub(self):
        matFlows = self.getMaterialFlowsByHub()

        hubDemands = {k: dict_mul(v, -7) for k, v in self.getMaterialInFlowsByHub().items()}
        hubPending = self.getMaterialPendingByHub()

        hubRequired = {h: {k: max(hubDemands[h].get(k, 0), hubPending[h].get(k, 0)) for k in hubDemands[h]} for h in hubDemands}

        hubInventories = {k: prun.storages.get(k, {}) for k in matFlows}
        hubSurpluses = {k: dict_add(hubInventories[k], dict_mul(hubRequired[k], -1)) for k in hubInventories}

        logging.info(f"COF {hubInventories.get('HRT', {}).get('COF', 0)}")

        return hubSurpluses


class Base:
    def __init__(self, empire, planet):
        self.empire: Empire = empire
        self.planet: prun.Planet = planet
        self.SiteId: str = ""
        self.buildings = {'CM': 1}
        self.production_lines = {}
        self.experts = {k: 0 for k in expertTypes}

        self.isCorpHQ = False
        self.isCompanyHQ = False

        self.defaultShipTypeIdx = 0

        self.supplyFrom = ""

        self._needsRepair = False

        self._shopping_list_cache = {}
        self._export_cache = {}

    def serialize(self):
        out = {}
        out['SiteId'] = self.SiteId
        out['planet'] = self.planet.PlanetNaturalId
        out['buildings'] = copy.copy(self.buildings)
        out['production_lines'] = copy.copy(self.production_lines)
        out['experts'] = copy.copy(self.experts)
        out['isCorpHQ'] = self.isCorpHQ
        out['isCompanyHQ'] = self.isCompanyHQ

        out['defaultShipTypeIdx'] = self.defaultShipTypeIdx
        out['supplyFrom'] = self.supplyFrom

        return out

    @classmethod
    def unserialize(cls, empire, inp):
        ret = cls(empire, prun.planets[inp['planet']])
        ret.SiteId = inp.get('SiteId', "")
        ret.buildings = inp.get('buildings', {'CM': 1})
        ret.production_lines = inp.get('production_lines', {})
        ret.experts = inp.get('experts', {k: 0 for k in expertTypes})
        ret.isCorpHQ = inp.get('isCorpHQ', False)
        ret.isCompanyHQ = inp.get('isCompanyHQ', False)
        ret.defaultShipTypeIdx = inp.get('defaultShipTypeIdx', 0)
        ret.supplyFrom = inp.get('supplyFrom', '')

        if ret.isCompanyHQ:
            empire.companyHQ = ret.planet

        return ret

    def announceChanges(self):
        self._shopping_list_cache.clear()
        self._export_cache.clear()

        pubsub.pub.sendMessage("empire_changed", empire_id=id(self.empire))
        pubsub.pub.sendMessage("base_changed", base_id=id(self))

    def setIsCorpHQ(self, state):
        if state != self.isCorpHQ:
            for b in self.empire.bases:
                b.isCorpHQ = False
            self.isCorpHQ = state

            if not self.planet.allowsCorpHQ():
                self.isCorpHQ = False

            self.announceChanges()

    def setIsCompanyHQ(self, state):
        if state != self.isCompanyHQ:
            for b in self.empire.bases:
                b.isCompanyHQ = False
            self.isCompanyHQ = state
            if state == True:
                self.empire.companyHQ = self.planet
            else:
                self.empire.companyHQ = None
            self.announceChanges()

    def setShipTypeIdx(self, idx):
        self.defaultShipTypeIdx = min(len(shipCapacities) - 1, max(0, idx))
        self.announceChanges()

    def setSupplyFrom(self, warehouseId: str):
        self.supplyFrom = warehouseId
        self.announceChanges()

    def getBuildingCount(self, ticker):
        return self.buildings.get(ticker, 0)

    def getTotalArea(self):
        a = 0
        for k, v in self.buildings.items():
            a += prun.buildings[k].AreaCost * v
        return a

    def getPermits(self):
        a = self.getTotalArea()
        if a <= 500:
            return 1
        elif a <= 750:
            return 2
        elif a <= 1000:
            return 3
        else:
            return 1000

    def getWorkerCapacities(self):
        return {
            "Pioneers": self.getBuildingCount('HB1') * 100 + self.getBuildingCount('HBB') * 75,
            "Settlers": self.getBuildingCount('HB2') * 100 + self.getBuildingCount('HBB') * 75 + self.getBuildingCount('HBC') * 75,
            "Technicians": self.getBuildingCount('HB3') * 100 + self.getBuildingCount('HBC') * 75 + self.getBuildingCount('HBM') * 75,
            "Engineers": self.getBuildingCount('HB4') * 100 + self.getBuildingCount('HBM') * 75 + self.getBuildingCount('HBL') * 75,
            "Scientists": self.getBuildingCount('HB5') * 100 + self.getBuildingCount('HBL') * 75
        }

    def getWorkersNeeded(self):
        ret = {
            "Pioneers": 0,
            "Settlers": 0,
            "Technicians": 0,
            "Engineers": 0,
            "Scientists": 0,
        }
        for k, n in self.buildings.items():
            b = prun.buildings[k]
            for wt in ret:
                ret[wt] += b.__dict__[wt] * n
        return ret

    def canIncrementBuilding(self, ticker):
        return self.getTotalArea() < 1000 and ticker != 'CM' and \
            ((ticker != 'FRM' and ticker != 'ORC') or self.planet.Fertility > -1.0)

    def canDecrementBuilding(self, ticker):
        return self.getBuildingCount(ticker) > 0 and ticker != 'CM'

    def getLimitsForBuilding(self, ticker):
        if ticker == 'CM':
            return (1, 1)
        surplusArea = 1000 - self.getTotalArea()
        buildingArea = prun.buildings[ticker].AreaCost
        currentCount = self.getBuildingCount(ticker)
        # logging.info(f"getLimitsForBuilding {ticker} {currentCount} {surplusArea} {buildingArea}")
        return (0, currentCount + surplusArea // buildingArea)

    def incrementBuilding(self, ticker):
        if self.canIncrementBuilding(ticker):
            if ticker in self.buildings:
                self.buildings[ticker] += 1
            else:
                self.buildings[ticker] = 1
            self.announceChanges()

    def decrementBuilding(self, ticker):
        if self.canDecrementBuilding(ticker):
            self.buildings[ticker] -= 1
            self.announceChanges()

    def setBuildingCount(self, ticker, count):
        # logging.info(f"setBuildingCount {ticker} {count}")
        lower, upper = self.getLimitsForBuilding(ticker)
        last_count = self.buildings.get(ticker, 0)
        self.buildings[ticker] = min(upper, max(lower, count))
        if self.buildings[ticker] != last_count:
            self.announceChanges()

    def removeBuilding(self, ticker):
        if ticker in self.buildings and ticker not in infrastructureBuildingTickers:
            del self.buildings[ticker]
            self.announceChanges()

    def recipesForBuilding(self, ticker):
        if ticker in ['COL', 'RIG', 'EXT']:
            return [r for r in self.planet.ResourceRecipes if ticker in r.StandardRecipeName]
        elif ticker in prun.buildings:
            return prun.buildings[ticker].Recipes
        else:
            return []

    def recipeIdsForBuilding(self, ticker) -> list[str]:
        return [r.BuildingRecipeId for r in self.recipesForBuilding(ticker)]

    def activeRecipeIdsForBuilding(self, ticker):
        return self.production_lines.get(ticker, {}).keys()

    def setRecipeQty(self, recipe_id, num_runs = 0):
        rec = prun.recipes[recipe_id]
        bui = rec.building

        if self.getBuildingCount(bui.Ticker) > 0:
            if bui.Ticker not in self.production_lines:
                self.production_lines[bui.Ticker] = {}

            self.production_lines[bui.Ticker][recipe_id] = num_runs

            self.announceChanges()

    def removeRecipe(self, recipe_id):
        rec = prun.recipes[recipe_id]
        bui = rec.building

        if bui.Ticker in self.production_lines:
            if recipe_id in self.production_lines[bui.Ticker]:
                del self.production_lines[bui.Ticker][recipe_id]
                self.announceChanges()

    def getRecipeQty(self, recipe_id):
        rec = prun.recipes[recipe_id]
        bui = rec.building
        if self.getBuildingCount(bui.Ticker) > 0:
            return self.production_lines[bui.Ticker].get(recipe_id, 0)
        else:
            return 0

    def getExpertLimits(self):
        totalExperts = sum(self.experts.values())
        maxAdditionalExperts = 6 - totalExperts

        return {k: (0, min(5, v + maxAdditionalExperts)) for k, v in self.experts.items()}

    def getExpertCount(self, expert_type):
        return self.experts.get(expert_type, 0)

    def setExpertCount(self, expert_type, count):
        limits = self.getExpertLimits()
        min_count, max_count = limits[expert_type]
        new_count = max(min_count, min(max_count, count))

        self.experts[expert_type] = new_count
        self.announceChanges()

    def getWorkerEfficiencies(self):
        capacities = self.getWorkerCapacities()
        needed = self.getWorkersNeeded()

        return {k: min(1.0, capacities[k] / needed[k]) if needed[k] > 0 else 0 for k in needed}

    def getBuildingEfficiency(self, ticker: str):
        bui = prun.buildings[ticker]
        weff = self.getWorkerEfficiencies()

        tot_workers = bui.Pioneers + bui.Settlers + bui.Technicians + bui.Engineers + bui.Scientists

        ret = sum((bui.__dict__[k] / tot_workers) * weff[k] for k in weff)

        if ticker in set(('FRM', 'ORC')):
            fertility_bonus = 1 + (self.planet.Fertility * 10/33)
            ret = ret * fertility_bonus

        if self.planet.COGCProgramStatus == 'ACTIVE':
            # logging.info(f"getBuildingEfficiency {self.planet.COGCPrograms[-1]}")
            cogc_category = self.planet.COGCPrograms[-1]['ProgramType']
            if cogc_category and bui.Expertise in cogc_category:
                ret = ret * 1.25

        expert_level = self.experts[bui.Expertise]
        ret = ret * expertMultiplierPerCount[expert_level]

        if self.isCorpHQ:
            ret = ret * 1.1

        faction_bonus = self.empire.getCompanyHQBonuses().get(bui.Expertise, 1.0)
        ret = ret * faction_bonus

        return ret

    def getStorageSize(self):
        return 1500 + 5000 * self.getBuildingCount('STO')

    def getStorageContents(self):
        return prun.storages.get(self.planet.PlanetNaturalId, {})

    def getFreeStorageSizes(self):
        current_m3, current_t = prun.sizesPerBasket(self.getStorageContents())
        cap = self.getStorageSize()
        return cap - current_m3, cap - current_t

    def getStorageAndWarehouseContents(self) -> dict[str, int]:
        return dict_add(self.getStorageContents(), prun.storages.get("W-" + self.planet.PlanetNaturalId, {}))

    def getSuggestedRepairIntervalDays(self):
        return self.planet.getSuggestedRepairIntervalDays()

    def getDailyMaterialInFlow(self, include_repairs = True):
        ret = {}

        # production
        for bui_ticker, recipes in self.production_lines.items():
            eff = self.getBuildingEfficiency(bui_ticker) * self.getBuildingCount(bui_ticker)

            if eff > 0:
                total_contribution = {}
                total_days = 0

                for recipe_key, runs in recipes.items():
                    if runs > 0:
                        recipe : prun.Recipe = prun.recipes[recipe_key]
                        recipe_days = recipe.DurationMs / MS_PER_DAY

                        total_days += recipe_days * runs
                        total_contribution = dict_add(total_contribution, dict_mul(recipe.Inputs, -runs))

                if total_days > 0:
                    ret = dict_add(ret, dict_mul(total_contribution, eff / total_days))

        # worker upkeeps
        workers_needed = self.getWorkersNeeded()
        worker_capacities = self.getWorkerCapacities()
        for k in workers_needed:
            needs_per_100 = prun.workforce_needs[k]
            if workers_needed[k] > 0 and worker_capacities[k] > 0:
                workers_available = min(workers_needed[k], worker_capacities[k])
                ret = dict_add(ret, dict_mul(needs_per_100, -workers_available / 100))

        # building repairs
        if include_repairs:
            for bui_ticker, n in self.buildings.items():
                if len(self.recipesForBuilding(bui_ticker)) > 0:
                    repair_cost = self.planet.realRepairCost(bui_ticker, self.getSuggestedRepairIntervalDays())
                    ret = dict_add(ret, dict_mul(repair_cost, -n / self.getSuggestedRepairIntervalDays()))

        return ret

    def getDailyMaterialOutFlow(self):
        ret = {}

        # production
        for bui_ticker, recipes in self.production_lines.items():
            eff = self.getBuildingEfficiency(bui_ticker) * self.getBuildingCount(bui_ticker)

            if eff > 0:
                total_contribution = {}
                total_days = 0

                for recipe_key, runs in recipes.items():
                    if runs > 0:
                        recipe : prun.Recipe = prun.recipes[recipe_key]
                        recipe_days = recipe.DurationMs / MS_PER_DAY

                        total_days += recipe_days * runs
                        total_contribution = dict_add(total_contribution, dict_mul(recipe.Outputs, runs))

                if total_days > 0:
                    ret = dict_add(ret, dict_mul(total_contribution, eff / total_days))

        return ret

    def getDailyMaterialFlow(self, include_repairs = True):
        return dict_add(self.getDailyMaterialInFlow(include_repairs), self.getDailyMaterialOutFlow())

    def getCurrentSupplyDays(self):
        flow = self.getDailyMaterialFlow(False)
        inv = self.getStorageAndWarehouseContents()

        if len(flow) == 0:
            return float('inf')

        return min((inv.get(k, 0) / -flow[k] for k in flow if flow[k] < 0))

    def getRecipeCogm(self, recipeKey):
        rec = prun.recipes[recipeKey]
        bui = rec.building
        bui_eff = self.getBuildingEfficiency(bui.Ticker)

        total_n = sum(v for k, v in rec.Outputs.items() if k not in cogmIgnores)

        if bui_eff > 0:
            prod_cost = prun.purchaseCostForBasket(rec.Inputs)
            daily_cost = 0

            # daily worker cost
            worker_upkeep = {}
            for k, v in prun.workforce_needs.items():
                needs_per_100 = v
                needs = dict_mul(needs_per_100, bui.__getattribute__(k) / 100)
                daily_cost += prun.purchaseCostForBasket(needs)

            # daily building depreciation
            repair_cost = dict_mul(self.planet.realRepairCost(bui.Ticker, self.getSuggestedRepairIntervalDays()), 1 / self.getSuggestedRepairIntervalDays())
            daily_cost += prun.purchaseCostForBasket(repair_cost)

            prod_cost += daily_cost * (rec.DurationMs / bui_eff) / MS_PER_DAY
        else:
            prod_cost = float('inf')

        cogm_per = prod_cost / total_n
        return {k: cogm_per for k in rec.Outputs if k not in cogmIgnores}

    def getRecipeCogmNumeric(self, recipeKey):
        cogm = self.getRecipeCogm(recipeKey)

        return next(iter(cogm.values()))


    def getRecipeProfitEstimate(self, recipeKey):
        rec = prun.recipes[recipeKey]
        bui = rec.building

        bui_eff = self.getBuildingEfficiency(bui.Ticker)
        ret = 0

        # material balance
        if bui_eff > 0:
            ret = prun.saleRevenueForBasket(rec.Outputs)
            ret -= prun.purchaseCostForBasket(rec.Inputs)
            ret *= MS_PER_DAY / (rec.DurationMs / bui_eff)

        # daily worker cost
        worker_upkeep = {}
        for k, v in prun.workforce_needs.items():
            needs_per_100 = v
            needs = dict_mul(needs_per_100, bui.__getattribute__(k) / 100)
            ret -= prun.purchaseCostForBasket(needs)

        # daily building depreciation
        repair_cost = dict_mul(self.planet.realRepairCost(bui.Ticker, self.getSuggestedRepairIntervalDays()), 1 / self.getSuggestedRepairIntervalDays())
        ret -= prun.purchaseCostForBasket(repair_cost)

        return ret

    def getBuildingDeltaFromOtherBase(self, other_base: Base | None):
        if not other_base:
            return {k: v for k, v in self.buildings.items()}
        return {k: v for k, v in dict_add(self.buildings, dict_mul(other_base.buildings, -1)).items() if v != 0}

    def getConstructionShoppingListVsOtherBase(self, other_base: Base | None):
        ret = {}
        for bui_ticker, count in self.getBuildingDeltaFromOtherBase(other_base).items():
            if count > 0:
                ret = dict_add(ret, dict_mul(self.planet.realBuildCost(bui_ticker), count))
        return ret

    def getTotalBuildCost(self):
        ret = {}
        for bui_ticker, count in self.buildings.items():
            if count > 0:
                ret = dict_add(ret, dict_mul(self.planet.realBuildCost(bui_ticker), count))
        return ret

    def getTotalCapitalCost(self):
        total_build_cost = self.getTotalBuildCost()
        return prun.purchaseCostForBasket(total_build_cost)

    def getDeltaCapitalCost(self, other_base: Base | None):
        if not other_base:
            return self.getTotalCapitalCost()
        return prun.purchaseCostForBasket(self.getConstructionShoppingListVsOtherBase(other_base))

    # def getSupplyListAndDuration(self, remaining_t, remaining_m3):
        # if remaining_t <= 0 or remaining_m3 <= 0:
        #     return {}, 0
        # inFlows = {k: v for k, v in dict_mul(self.getDailyMaterialFlow(), -1).items() if v > 0}
        # t_per_day = sum(prun.materials[k].Weight * v for k, v in inFlows.items())
        # m3_per_day = sum(prun.materials[k].Volume * v for k, v in inFlows.items())

        # if t_per_day <= 0 or m3_per_day <= 0:
        #     return {}, 0

        # total_days = min(remaining_t / t_per_day, remaining_m3 / m3_per_day)
        # total_list = {k: 1 if v < 1 else math.floor(v) for k, v in dict_mul(inFlows, total_days).items()}

        # return total_list, total_days

    def getSupplyListAndDuration(self, remaining_t, remaining_m3, target_d = DEFAULT_TARGET_D):
        cache_key = (remaining_t, remaining_m3, target_d)
        if cache_key in self._shopping_list_cache:
            # logging.info(f"{self} getSupplyListAndDuration cache")
            return self._shopping_list_cache[cache_key]

        # logging.info(f"{self} getSupplyListAndDuration compute")
        if remaining_m3 <= 0 or remaining_t <= 0:
            return {}, 0

        have = self.getStorageAndWarehouseContents()
        need = {}
        want = {}

        remaining_sto_m3, remaining_sto_t = self.getFreeStorageSizes()
        remaining_m3 = min(remaining_m3, remaining_sto_m3)
        remaining_t = min(remaining_t, remaining_sto_t)

        repair_cost = {}
        # add mats needed for repairs
        for bui_ticker, n in self.buildings.items():
            if len(self.recipesForBuilding(bui_ticker)) > 0:
                repair_cost = self.planet.realRepairCost(bui_ticker, self.getSuggestedRepairIntervalDays())
                need = dict_add(need, dict_mul(repair_cost, n))

        # add desired supply
        dailyMaterialFlow = self.getDailyMaterialFlow(False)
        tgt_supply = dict_mul(dailyMaterialFlow, -target_d)
        tgt_supply = {k: v for k, v in tgt_supply.items() if v > 0}

        # for every recipe requested by this base ensure we are asking for enough
        # to run at least 2n runs of everything
        min_supply = {}
        for bui_ticker, recipes in self.production_lines.items():
            if self.buildings.get(bui_ticker, 0) > 0:
                for recipe_key, runs in recipes.items():
                    if runs > 0:
                        recipe : prun.Recipe = prun.recipes[recipe_key]
                        for mat, qty in recipe.Inputs.items():
                            if dailyMaterialFlow[mat] != 0:
                                min_supply[mat] = min_supply.get(mat, 0) + qty * runs * 2

        for mat, qty in min_supply.items():
            if tgt_supply.get(mat, 0) < qty:
                tgt_supply[mat] = qty

        # logging.info(tgt_supply)

        want = {k: v for k, v in tgt_supply.items() if v > 0}
        for k in want:
            if want[k] < 2:
                want[k] = 2

        # shift 2 of everything from want to need
        for k in want:
            want[k] = want[k] - 2
            need[k] = need.get(k, 0) + 2

        # cancel out have with need
        for k in need:
            if k in have:
                n_cancel = min(have[k], need[k])
                have[k] = have[k] - n_cancel
                need[k] = need[k] - n_cancel

        # cancel out have with want
        for k in want:
            if k in have:
                n_cancel = min(have[k], want[k])
                have[k] = have[k] - n_cancel
                want[k] = want[k] - n_cancel

        # start a cart
        cart = {k: v for k, v in need.items()}
        for k, v in cart.items():
            remaining_m3 -= v * prun.materials[k].Volume
            remaining_t -= v * prun.materials[k].Weight

        will_have = dict_add(self.getStorageAndWarehouseContents(), cart)
        satisf = {k: will_have.get(k, 0) / v for k, v in tgt_supply.items() if v > 0}

        # fill the cart
        while remaining_m3 > 0 and remaining_t > 0 and any((z > 0 for z in want.values())):
            # find the lowest satisf item in our want set
            next_item, next_satisf = min(((k, satisf.get(k)) for k in satisf), key=lambda x: x[1])
            if next_satisf >= 1:
                break

            # add a bit of next_item to the cart
            mat = prun.materials[next_item]
            dvol = mat.Volume
            dwgt = mat.Weight
            dn = max(1, math.floor(min(want[next_item], min(1, remaining_m3) / dvol, min(1, remaining_t) / dwgt)))

            cart[next_item] = cart.get(next_item, 0) + dn
            will_have[next_item] = will_have.get(next_item, 0) + dn
            want[next_item] = want[next_item] - dn
            satisf[next_item] = will_have[next_item] / tgt_supply[next_item]
            remaining_m3 -= dn * dvol
            remaining_t -= dn * dwgt

        # trim cart overflow
        if len(want):
            while remaining_m3 < 0 or remaining_t < 0:
                # find an item
                next_item, _ = max(((k, cart[k]) for k in cart if k in want and k not in repair_cost), default=(None, None), key=lambda x: x[1])
                if not next_item:
                    break
                # remove a bit of next_item from the cart
                mat = prun.materials[next_item]
                dvol = mat.Volume
                dwgt = mat.Weight
                dn = -1

                cart[next_item] = cart.get(next_item, 0) + dn
                will_have[next_item] = will_have.get(next_item, 0) + dn
                remaining_m3 -= dn * dvol
                remaining_t -= dn * dwgt

        # compute delta-days
        current_days = self.getCurrentSupplyDays()
        flow = self.getDailyMaterialFlow(False)
        new_days = min((will_have.get(k, 0) / -flow[k] for k in flow if flow[k] < 0), default=0)

        ret = {k: v for k, v in cart.items() if v > 0}, new_days - current_days
        self._shopping_list_cache[cache_key] = ret

        return ret

    def getAvailableExports(self, remaining_t = float('inf'), remaining_m3 = float('inf'), target_d = DEFAULT_TARGET_D):
        cache_key = (remaining_t, remaining_m3, target_d)
        if cache_key in self._export_cache:
            return self._export_cache[cache_key]

        min_stock = {}

        repair_cost = {}
        # add mats needed for repairs
        for bui_ticker, n in self.buildings.items():
            if len(self.recipesForBuilding(bui_ticker)) > 0:
                repair_cost = self.planet.realRepairCost(bui_ticker, self.getSuggestedRepairIntervalDays())
                min_stock = dict_add(min_stock, dict_mul(repair_cost, n))

        # for every recipe requested by this base ensure we are asking for enough
        # to run at least 2n runs of everything
        min_supply = {}
        for bui_ticker, recipes in self.production_lines.items():
            if self.buildings.get(bui_ticker, 0) > 0:
                for recipe_key, runs in recipes.items():
                    if runs > 0:
                        recipe : prun.Recipe = prun.recipes[recipe_key]
                        for mat, qty in recipe.Inputs.items():
                            min_supply[mat] = min_supply.get(mat, 0) + qty * runs * 2
        min_stock = dict_add(min_stock, min_supply)

        # for consumables ensure we have at least enough for target days
        worker_reqs = {}
        workers_needed = self.getWorkersNeeded()
        worker_capacities = self.getWorkerCapacities()
        for k in workers_needed:
            needs_per_100 = prun.workforce_needs[k]
            if workers_needed[k] > 0 and worker_capacities[k] > 0:
                workers_available = min(workers_needed[k], worker_capacities[k])
                worker_reqs = dict_add(worker_reqs, dict_mul(needs_per_100, workers_available / 100))
        for k, v in worker_reqs.items():
            min_stock[k] = max(min_stock.get(k, 0), math.ceil(v * target_d))

        ret = dict_add(self.getStorageContents(), dict_mul(min_stock, -1))

        # only be exporting things with positive net flow
        dailyMaterialFlow = self.getDailyMaterialFlow()
        ret = {k: v for k, v in ret.items() if v > 0 and dailyMaterialFlow.get(k, 0) > 0}

        self._export_cache[cache_key] = ret

        return ret


    def getTotalStartupCost(self, cap_t = 500, cap_m3 = 500):
        total_build_cost = self.getTotalBuildCost()
        build_cost_m3 = sum(v * prun.materials[k].Volume for k, v in total_build_cost.items())
        build_cost_t = sum(v * prun.materials[k].Weight for k, v in total_build_cost.items())

        supply_list, _ = self.getSupplyListAndDuration(cap_t - build_cost_t, cap_m3 - build_cost_m3)

        return prun.purchaseCostForBasket(dict_add(total_build_cost, supply_list))

    def getExpectedDailyProfit(self):
        daily_flow = self.getDailyMaterialFlow()
        daily_in = {k: v for k, v in dict_mul(daily_flow, -1).items() if v > 0}
        daily_out = {k: v for k, v in dict_mul(daily_flow, 1).items() if v > 0}

        return prun.saleRevenueForBasket(daily_out) - prun.purchaseCostForBasket(daily_in)

    def getExpectedDailyProfitChange(self, other_base: Base | None):
        if not other_base:
            return self.getExpectedDailyProfit()
        daily_flow = dict_add(self.getDailyMaterialFlow(), dict_mul(other_base.getDailyMaterialFlow(), -1))
        daily_in = {k: v for k, v in dict_mul(daily_flow, -1).items() if v > 0}
        daily_out = {k: v for k, v in dict_mul(daily_flow, 1).items() if v > 0}

        return prun.saleRevenueForBasket(daily_out) - prun.purchaseCostForBasket(daily_in)




if __name__ == '__main__':
    e = Empire()
    b = e.createBase('VH-331a')
    b.incrementBuilding('HB1')
    b.incrementBuilding('HB1')
    b.incrementBuilding('FRM')
    b.incrementBuilding('RIG')
    b.incrementBuilding('FP')

    b.setRecipeQty("(VH-331a)@RIG=>8xH2O", 1)
    b.setRecipeQty("1xH2O@FRM=>12xNUT", 1)
    b.setRecipeQty("1xH2O@FRM=>2xBEA", 6)
    b.setRecipeQty("1xH2O@FRM=>4xGRN", 3)
    b.setRecipeQty("1xGRN 1xBEA 1xNUT@FP=>10xRAT", 3)
    b.setRecipeQty("10xH2O@FP=>7xDW", 4)

    print(b.buildings)
    print(b.getWorkerCapacities())
    print(b.getWorkersNeeded())

    print(b.getDailyMaterialFlow())

    import IPython
    IPython.embed()