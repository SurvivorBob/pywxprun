from __future__ import annotations

import json
import math
import copy

import models.util

import logging
logging.getLogger().setLevel(logging.INFO)

import configparser
config = configparser.ConfigParser()
config.read("pywxprun.cfg")

fio_api_key = config['Config']['APIKey']
fio_un = config['Config']['UserName']

import requests
_requests_session = requests.Session()

import time
import sqlite3
requests_cache_conn = sqlite3.Connection("http_cache.db3")
requests_cache_conn.execute("create table if not exists cache (path, last_time, last_value)")
requests_cache_conn.execute("create table if not exists cache2 (path, last_time, last_value)")
requests_cache_conn.commit()

import threading

fio_api_base = "https://rest.fnar.net"
def fio_get(path):
    if threading.current_thread() != threading.main_thread():
        _requests_cache_conn = sqlite3.Connection("http_cache.db3")
    else:
        _requests_cache_conn = requests_cache_conn
    z = _requests_cache_conn.execute("select last_time, last_value from cache where path = ?", (path,)).fetchone()
    if z:
        last_time, last_value = z
    else:
        last_time, last_value = None, None
    if last_time is None or last_time < time.time() - 600:
        try:
            resp = _requests_session.get(fio_api_base + path, headers={"Authorization": fio_api_key}, timeout=15)
            if resp.status_code == 200:
                _requests_cache_conn.execute("insert or replace into cache (path, last_time, last_value) values (?, ?, ?)", (path, time.time(), json.dumps(resp.json())))
                _requests_cache_conn.commit()
                return resp.json()
        except:
            if last_value is not None:
                return json.loads(last_value)
            return None
    if last_value is not None:
        return json.loads(last_value)
    return None

fio2_api_base = "https://api.fnar.net"
def fio2_get(path):
    if threading.current_thread() != threading.main_thread():
        _requests_cache_conn = sqlite3.Connection("http_cache.db3")
    else:
        _requests_cache_conn = requests_cache_conn
    z = _requests_cache_conn.execute("select last_time, last_value from cache2 where path = ?", (path,)).fetchone()
    if z:
        last_time, last_value = z
    else:
        last_time, last_value = None, None
    if last_time is None or last_time < time.time() - 600:
        try:
            resp = _requests_session.get(fio2_api_base + path, headers={"Authorization": "FIOAPIKey " + fio_api_key}, timeout=15)
            if resp.status_code == 200:
                _requests_cache_conn.execute("insert or replace into cache2 (path, last_time, last_value) values (?, ?, ?)", (path, time.time(), json.dumps(resp.json())))
                _requests_cache_conn.commit()
                return resp.json()
        except:
            if last_value is not None:
                return json.loads(last_value)
            return None
    if last_value is not None:
        return json.loads(last_value)
    return None

class Material:
    def __init__(self, dat):
        self.MaterialId: str = ""
        self.Name: str = ""
        self.CategoryName: str = ""
        self.Ticker: str = ""
        self.Weight: float = 0
        self.Volume: float = 0
        self.__dict__.update(dat)

        self.markets : dict[str, Market] = {}

    def __str__(self):
        return self.Ticker

    def __repr__(self):
        return f"<Material {self.Ticker} ({id(self)})>"

    def getBuyCostForQtyInMarket(self, n, mkt = None):
        if not mkt:
            mkt = config['Config']['DefaultMarket']
        mkt2 = config['Config']['BackupMarket']
        p = self.markets[mkt].getAskPriceAtDepth(n)
        if p == self.markets[mkt].WidePriceBandHigh:
            p = self.markets[mkt2].getAskPriceAtDepth(n)
        return p * n

    def getSellCostForQtyInMarket(self, n, mkt = None):
        if not mkt:
            mkt = config['Config']['DefaultMarket']
        if self.Ticker in moneyPrintingMatTickers:
            return self.markets[mkt].MMBuy * n
        return self.markets[mkt].getPrice() * n

materials : dict[str, Material] = {}
moneyPrintingMatTickers = set(('EDC', 'IDC'))

class Market:
    def __init__(self, dat):
        self.MaterialTicker = ""
        self.ExchangeCode = ""
        self.Ask: float = 0
        self.Bid: float = 0
        self.Supply: int = 0
        self.Demand: int = 0

        self.MMBuy: None | float = None
        self.MMSell: None | float = None

        self.WidePriceBandHigh: float = float('inf')

        self.BuyingOrders = []
        self.SellingOrders = []

        self.__dict__.update(dat)

        self.BuyingOrders.sort(key=lambda x: x['ItemCost'], reverse=True)
        self.SellingOrders.sort(key=lambda x: x['ItemCost'], reverse=False)

    def getPrice(self):
        if self.Supply > 0:
            return self.Ask
        else:
            return self.WidePriceBandHigh

    def getAskPriceAtDepth(self, n):
        if self.Supply == 0:
            return self.WidePriceBandHigh
        elif n >= self.Supply:
            return self.SellingOrders[-1]['ItemCost']
        else:
            depthRemaining = n
            for order in self.SellingOrders:
                if order['ItemCount'] is None or order['ItemCount'] > depthRemaining:
                    return order['ItemCost']
                else:
                    depthRemaining -= order['ItemCount']
            return self.SellingOrders[-1]['ItemCost']

def purchaseCostForBasket(basket: dict[str, int]):
    return sum(materials[k].getBuyCostForQtyInMarket(v) for k, v in basket.items())

def saleRevenueForBasket(basket: dict[str, int]):
    return sum(materials[k].getSellCostForQtyInMarket(v) for k, v in basket.items())

def sizesPerBasket(basket: dict[str, int]):
    return sum(v * materials[k].Volume for k, v in basket.items()), sum(v * materials[k].Weight for k, v in basket.items())

class Recipe:
    def __init__(self, dat):
        self.Inputs = []
        self.Outputs = []
        self.DurationMs: int = 1
        self.StandardRecipeName = ""
        self.BuildingRecipeId = ""
        self.building: Building = None

        self.__dict__.update(dat)

        self.Inputs = {x['CommodityTicker']: x['Amount'] for x in self.Inputs}
        self.Outputs = {x['CommodityTicker']: x['Amount'] for x in self.Outputs}

    def __repr__(self):
        return f"<Recipe {self.BuildingRecipeId} ({id(self)})>"

    def __str__(self):
        return self.StandardRecipeName

class Building:
    def __init__(self, dat):
        self.Ticker = ""
        self.Expertise = ""
        self.AreaCost: int = 0
        self.Pioneers: int = 0
        self.Settlers: int = 0
        self.Technicians: int = 0
        self.Engineers: int = 0
        self.Scientists: int = 0
        self.BuildingCosts = []
        self.Recipes = []

        self.__dict__.update(dat)

        self.BuildingCosts = {x['CommodityTicker']: x['Amount'] for x in self.BuildingCosts}
        self.Recipes = [Recipe(x) for x in self.Recipes]

    def __repr__(self):
        return f"<Building {self.Ticker} ({id(self)})>"

    def __str__(self):
        return self.Ticker

buildings: dict[str, Building] = {}
recipes: dict[str, Recipe] = {}

def buildingMaterialSortOrder(m):
    return {
        "MCG": 0,
        "AEF": 1,
        "SEA": 2,
        "HSE": 3,
        "INS": 4,
        "TSH": 5,
        "MGC": 6,
        "BL": 7
    }.get(m, 99)

starterPlanetNames = [
    "Deimos",
    "Phobos",
    "Promitor",
    "Avalon",
    "Berthier",
    "Nova Honshu",
    "Montem",
    "Vallis",
    "Prism",
    "Proxion",
    "Gibson",
    "Umbra",
    "Katoa"
]

class Planet:
    def __init__(self, dat):
        self.PlanetNaturalId = ""
        self.PlanetName = ""
        self.FactionCode: str | None = None
        self.__dict__.update(dat)

        self.BuildRequirements = {x['MaterialTicker']: x['MaterialAmount'] for x in self.BuildRequirements}

        self.ResourceRecipes = []
        self.DailyResourcesSummary = {}

        for res in self.Resources:
            mat = materials[res['MaterialId']]
            mat_bui = {
                "GASEOUS": "COL",
                "MINERAL": "EXT",
                "LIQUID": "RIG"
            }[res["ResourceType"]]

            new_recipe = copy.copy(buildings[mat_bui].Recipes[0])

            daily_extraction = res['Factor'] * 100 * {
                "GASEOUS": 0.6,
                "MINERAL": 0.7,
                "LIQUID": 0.7
            }[res["ResourceType"]]

            self.DailyResourcesSummary[mat.Ticker] = (daily_extraction, mat_bui)

            units_per_cycle = daily_extraction * (new_recipe.DurationMs / 86400000)
            units_per_recipe = math.ceil(units_per_cycle)
            scale_factor = units_per_recipe / units_per_cycle

            new_recipe.Outputs = {mat.Ticker: units_per_recipe}
            new_recipe.DurationMs = new_recipe.DurationMs * scale_factor

            new_recipe.StandardRecipeName = f"({self.PlanetNaturalId}){mat_bui}:=>{units_per_recipe}x{mat.Ticker}"
            new_recipe.BuildingRecipeId = f"({self.PlanetNaturalId})@{mat_bui}=>{units_per_recipe}x{mat.Ticker}"
            new_recipe.RecipeName = f"({self.PlanetNaturalId})=>{units_per_recipe}x{mat.Ticker}"

            recipes[new_recipe.BuildingRecipeId] = new_recipe
            self.ResourceRecipes.append(new_recipe)

    def __repr__(self):
        return f"<Planet {self.PlanetNaturalId}>"

    def allowsCorpHQ(self) -> bool:
        return self.PlanetName not in starterPlanetNames

    def buildingMaterials(self):
        br = self.BuildRequirements
        cmb = buildings['CM'].BuildingCosts
        return set(br.keys()) - set(cmb.keys())

    def realBuildCost(self, ticker_or_building) -> dict:
        building : Building = None
        if type(ticker_or_building) == str:
            building = buildings[ticker_or_building]
        else:
            building = ticker_or_building

        ret = copy.copy(building.BuildingCosts)

        extra_bm = self.buildingMaterials()
        if 'MCG' in extra_bm:
            ret['MCG'] = building.AreaCost * 4
        if 'AEF' in extra_bm:
            ret['AEF'] = math.ceil(building.AreaCost / 3)
        if 'SEA' in extra_bm:
            ret['SEA'] = building.AreaCost
        if 'HSE' in extra_bm:
            ret['HSE'] = 1
        if 'MGC' in extra_bm:
            ret['MGC'] = 1
        if 'BL' in extra_bm:
            ret['BL'] = 1
        if 'INS' in extra_bm:
            ret['INS'] = building.AreaCost * 10
        if 'TSH' in extra_bm:
            ret['TSH'] = 1

        return ret

    def realReclaimableCost(self, ticker_or_building, days) -> dict:
        bc = self.realBuildCost(ticker_or_building)
        rc = {}
        for k in bc:
            v = bc[k]
            rc[k] = math.floor(v * ((180. - min(180., days)) / 180.))
        return rc

    def realRepairCost(self, ticker_or_building, days) -> dict:
        bc = self.realBuildCost(ticker_or_building)
        rc = self.realReclaimableCost(ticker_or_building, days)

        return {k: bc[k] - rc.get(k, 0) for k in bc}

    def cogcType(self):
        if len(self.COGCPrograms) and self.COGCProgramStatus == 'ACTIVE':
            program = max(self.COGCPrograms, key=lambda x: x['StartEpochMs'])
            return program['ProgramType']
        return self.COGCProgramStatus

    def dailyResourcesPerArea(self) -> dict:
        return {k: v[0] / (buildings[v[1]].AreaCost) for k, v in self.DailyResourcesSummary.items()}

planets = {}
planets_trie = models.util.PrefixTree()
workforce_needs = {}

def planet_search(name_or_id_prefix: str) -> list[Planet]:
    found = planets_trie.search(name_or_id_prefix)

    key_set = set()
    ret = []
    for p in found:
        if p.PlanetNaturalId not in key_set:
            ret.append(p)
            key_set.add(p.PlanetNaturalId)
    return ret

class StarSystem:
    def __init__(self, dat):
        self.SystemId : str = ''
        self.NaturalId : str = ''
        self.Name : str = ''
        self.Connections : list[str] = ''
        self.PositionX : float = 0
        self.PositionY : float = 0
        self.PositionZ : float = 0

        self.__dict__.update(dat)

        self.connectionsWithDists : list[tuple[StarSystem, float]] = []

        self._connected_distance_to_cache : dict[StarSystem, float] = {}

    def __repr__(self):
        return f"<StarSystem {self.NaturalId}>"

    def distanceTo(self, other: StarSystem):
        dx = self.PositionX - other.PositionX
        dy = self.PositionY - other.PositionY
        dz = self.PositionZ - other.PositionZ
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def connectedDistanceTo(self, other: StarSystem):
        if self == other or self.SystemId == other.SystemId:
            return 0

        if other in self._connected_distance_to_cache:
            return self._connected_distance_to_cache[other]

        # dijkstra our way there or something
        finalized: dict[str, tuple[StarSystem, float]] = {}
        spotted: dict[str, tuple[StarSystem, float]] = {}

        current: StarSystem = self
        finalized[current.NaturalId] = (current, 0)
        for s, dist in current.connectionsWithDists:
            if s.NaturalId not in finalized:
                spotted[s.NaturalId] = (s, min(spotted.get(s.NaturalId, (None, float('inf')))[1], finalized[current.NaturalId][1] + dist))

        def find_min_s(d: dict[str, tuple[StarSystem, float]]):
            least_k = None
            least_v = float('inf')

            for k, v in d.items():
                if v[1] < least_v:
                    least_k = k
                    least_v = v[1]
            return d[least_k][0]

        while len(spotted):
            current = find_min_s(spotted)
            finalized[current.NaturalId] = (current, spotted[current.NaturalId][1])

            if current.NaturalId == other.NaturalId:
                ret = finalized[current.NaturalId][1]
                self._connected_distance_to_cache[other] = ret
                return ret

            del spotted[current.NaturalId]

            for s, dist in current.connectionsWithDists:
                if s.NaturalId not in finalized:
                    spotted[s.NaturalId] = (s, min(spotted.get(s.NaturalId, (None, float('inf')))[1], finalized[current.NaturalId][1] + dist))

        return float('inf')

systems : dict[str, StarSystem] = {}
systems_trie = models.util.PrefixTree()

class ExchangeStation:
    def __init__(self, dat):
        self.WarehouseId : str = ''
        self.NaturalId : str = ''

        self.__dict__.update(dat)

exchangeWarehouses : dict[str, ExchangeStation] = {}

storages : dict[str, dict[str, int]] = {}

loaded = False
def reload_all():
    materials.clear()
    logging.info("loading materials")
    _all_materials = fio_get("/material/allmaterials")
    for mat in _all_materials:
        m = Material(mat)
        materials[m.MaterialId] = m
        materials[m.Ticker] = m

    logging.info("loading exchange data")
    _exchange_data = fio_get("/exchange/full")
    for dat in _exchange_data:
        mkt = Market(dat)
        mat = materials[mkt.MaterialTicker]
        mat.markets[mkt.ExchangeCode] = mkt

    logging.info("loading building data")
    _building_data = fio_get("/building/allbuildings")
    buildings.clear()
    recipes.clear()
    for dat in _building_data:
        bui = Building(dat)
        buildings[bui.Ticker] = bui
        buildings[bui.Name] = bui
        for rec in bui.Recipes:
            if rec.BuildingRecipeId in recipes:
                logging.warn(f"duplicate recipe key {rec.BuildingRecipeId}")
            recipes[rec.BuildingRecipeId] = rec
            recipes[rec.StandardRecipeName] = rec
            rec.building = bui

    systems.clear()
    logging.info("loading system data")
    _system_data = fio2_get("/map/systems")
    for dat in _system_data:
        sys = StarSystem(dat)
        systems[sys.SystemId] = sys
        systems_trie.insert(sys.NaturalId, sys)
        systems_trie.insert(sys.Name, sys)

    logging.info("computing system distances")
    for sys in systems.values():
        for other_k in sys.Connections:
            other_sys = systems[other_k]
            sys.connectionsWithDists.append((other_sys, sys.distanceTo(other_sys)))


    planets.clear()
    logging.info("loading planet data")
    _planet_data = fio_get("/planet/allplanets/full")
    for dat in _planet_data:
        pla = Planet(dat)
        planets[pla.PlanetNaturalId] = pla
        planets_trie.insert(pla.PlanetNaturalId, pla)
        planets_trie.insert(pla.PlanetName, pla)

    logging.info("loading workforce needs")
    _worker_upkeep_data = fio_get("/global/workforceneeds")
    workforce_needs.clear()
    for dat in _worker_upkeep_data:
        workforce_needs[{
            "PIONEER": "Pioneers",
            "SETTLER": "Settlers",
            "TECHNICIAN": "Technicians",
            "ENGINEER": "Engineers",
            "SCIENTIST": "Scientists",
        }[dat["WorkforceType"]]] = {n["MaterialTicker"]: n["Amount"] for n in dat["Needs"]}

    logging.info("loading exchange stations")
    exchangeWarehouses.clear()
    _exchange_station_data = fio_get("/exchange/station")
    for dat in _exchange_station_data:
        sta = ExchangeStation(dat)
        exchangeWarehouses[sta.WarehouseId] = sta

    if len(fio_api_key) and len(fio_un):
        logging.info("loading player sites")
        _sites_data = fio_get(f"/sites/{fio_un}")

        _site_id_planet_id_map = {x['SiteId']: x['PlanetIdentifier'] for x in _sites_data}

        logging.info("loading player warehouses")
        _warehouse_data = fio_get(f"/sites/warehouses/{fio_un}")
        _warehouse_id_planet_id_map = {x['StoreId']: x['LocationNaturalId'] for x in _warehouse_data}

        logging.info("loading player storages")
        storages.clear()
        _storage_data = fio_get(f"/storage/{fio_un}")
        for dat in _storage_data:
            tgt_id = dat.get('AddressableId', '')
            tgt = None
            if tgt_id in exchangeWarehouses:
                tgt = exchangeWarehouses[tgt_id]
            elif tgt_id in _site_id_planet_id_map:
                tgt = _site_id_planet_id_map[tgt_id]
            elif tgt_id in _warehouse_id_planet_id_map:
                tgt = "W-" + _warehouse_id_planet_id_map[tgt_id]

            if tgt:
                inv = {}
                for item in dat['StorageItems']:
                    inv[item['MaterialTicker']] = item['MaterialAmount']
                storages[tgt] = inv


if __name__ == '__main__':
    logging.info("loading ipython shell")
    import IPython
    IPython.embed()