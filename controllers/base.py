import wx
import pubsub.pub

import math

import resources.gui
import models.empire
import models.prun

import controllers.controller

from models.util import dict_add, dict_mul

class BaseController(controllers.controller.Controller):
    def __init__(self, app, base, *args, **kw):
        super().__init__(app, base, *args, **kw)

        self.app = app
        self.base: models.empire.Base = base
        self.view: resources.gui.BaseView = resources.gui.BaseView(None)
        self.acceptingUpdates = True

        self.productionBuildingControllers : list[ProductionBuildingController] = []
        self.availableBuildings = []

        self.app.RegisterController(self)

        self.view.Bind(wx.EVT_CLOSE, self.onClose)
        self.view.buttonAddBuilding.Bind(wx.EVT_BUTTON, self.onAddNewBuildingPressed)
        self.view.choiceNewBuilding.Bind(wx.EVT_CHOICE, self.onSelectedBuildingChanged)
        self.view.radioBoxCargoBay.Bind(wx.EVT_RADIOBOX, self.onCargoBayTypeChanged)
        self.view.checkBoxCompanyHQ.Bind(wx.EVT_CHECKBOX, self.onCompanyHQToggled)
        self.view.checkBoxCorpHQ.Bind(wx.EVT_CHECKBOX, self.onCorpHQToggled)

        self.view.checkBoxCorpHQ.Enabled = self.base.planet.allowsCorpHQ()

        self.infrastructureSpinners: dict[str, wx.SpinCtrl] = {}
        self.expertSpinners: dict[str, wx.SpinCtrl] = {}
        self.setUpSpinnerData()

        self.reloadViewFromModel()

        pubsub.pub.subscribe(self.onEmpireChanged, "empire_changed")
        pubsub.pub.subscribe(self.onBaseChanged, "base_changed")

        self.view.Show()

    def onUnregister(self, *args, **kw):
        self.view.Destroy()
        pubsub.pub.sendMessage("base_window_closed", base_id=id(self))
        return super().onUnregister(*args, **kw)

    def onClose(self, _):
        for c in self.productionBuildingControllers:
            c.onClose()
        self.productionBuildingControllers.clear()
        pubsub.pub.unsubscribe(self.onEmpireChanged, "empire_changed")
        pubsub.pub.unsubscribe(self.onBaseChanged, "base_changed")
        self.app.UnregisterController(self)

    def setUpSpinnerData(self):
        for i in models.empire.infrastructureBuildingTickers:
            self.infrastructureSpinners[i] = self.view.__getattribute__(f'spinCtrl{i}')

        for e in models.empire.expertTypes:
            self.expertSpinners[e] = self.view.__getattribute__(f'spinCtrlExperts{e}')

        for k, v in self.infrastructureSpinners.items():
            def onSpinCtrlUpdated(z):
                def f(e: wx.SpinEvent):
                    self.base.setBuildingCount(z, e.GetPosition())
                return f

            v.Bind(wx.EVT_SPINCTRL, onSpinCtrlUpdated(k))

        for k, v in self.expertSpinners.items():
            def onSpinCtrlUpdated(z):
                def f(e: wx.SpinEvent):
                    self.base.setExpertCount(z, e.GetPosition())
                return f

            v.Bind(wx.EVT_SPINCTRL, onSpinCtrlUpdated(k))

    def onEmpireChanged(self, empire_id):
        if empire_id == id(self.base.empire) and self.acceptingUpdates:
            self.acceptingUpdates = False
            self.reloadViewFromModel()
            self.acceptingUpdates = True

    def onBaseChanged(self, base_id):
        if base_id == id(self.base) and self.acceptingUpdates:
            self.acceptingUpdates = False
            self.reloadViewFromModel()
            self.acceptingUpdates = True

    def onAddNewBuildingPressed(self, event: wx.CommandEvent):
        if len(self.availableBuildings) > 0:
            i = self.view.choiceNewBuilding.Selection
            if i != wx.NOT_FOUND:
                buildingTicker = self.availableBuildings[i]
                self.base.setBuildingCount(buildingTicker, 1)
                self.view.buttonAddBuilding.Enabled = False

    def onSelectedBuildingChanged(self, event: wx.CommandEvent):
        self.view.buttonAddBuilding.Enabled = (event.Selection != wx.NOT_FOUND)

    def onCargoBayTypeChanged(self, event: wx.CommandEvent):
        self.base.setShipTypeIdx(event.Int)
        # self.reloadShoppingListFromModel()
        # self.reloadSummaryViewFromModel()

    def onCompanyHQToggled(self, event: wx.CommandEvent):
        self.base.setIsCompanyHQ(event.IsChecked())

    def onCorpHQToggled(self, event: wx.CommandEvent):
        self.base.setIsCorpHQ(event.IsChecked())

    def reloadResourcesFromModel(self):
        ct = self.view.listCtrlResources
        ct.ClearAll()
        ct.InsertColumn(0, "Mat")
        ct.InsertColumn(1, "Amt/Day")
        ct.InsertColumn(2, "Bldg")
        rsc_list = [(mat, round(dat[0], 2), dat[1]) for mat, dat in self.base.planet.DailyResourcesSummary.items()]
        rsc_list.sort(key=lambda x: x[1], reverse=True)
        for x in rsc_list:
            ct.Append(x)

    def reloadMaterialFlowsFromModel(self):
        ct = self.view.listCtrlMaterialFlows
        ct.ClearAll()
        ct.InsertColumn(0, "Mat")
        ct.InsertColumn(1, "Amt/Day")
        flw_list = [(k, round(v, 2)) for k, v in self.base.getDailyMaterialFlow().items()]
        flw_list.sort(key=lambda x: x[1], reverse=True)
        for x in flw_list:
            ct.Append(x)

    def reloadWorkerStatisticsFromModel(self):
        workersNeeded = self.base.getWorkersNeeded()
        workerCapacities = self.base.getWorkerCapacities()

        workerSurpluses = dict_add(workerCapacities, dict_mul(workersNeeded, -1))

        ct = self.view.listCtrlWorkforce
        ct.ClearAll()
        ct.InsertColumn(0, "Workers")
        ct.InsertColumn(1, "Cap")
        ct.InsertColumn(2, "Req")
        ct.InsertColumn(3, "Avail")

        for z in models.empire.workerTypeOrdering:
            ct.Append((z, workerCapacities[z], workersNeeded[z], workerSurpluses[z]))


    def reloadSpinnersFromModel(self):
        for k, spn in self.infrastructureSpinners.items():
            lower, upper = self.base.getLimitsForBuilding(k)
            cur = self.base.getBuildingCount(k)

            spn.SetValue(cur)
            spn.SetMin(lower)
            spn.SetMax(upper)

        expertLimits = self.base.getExpertLimits()
        for k, spn in self.expertSpinners.items():
            lower, upper = expertLimits[k]
            cur = self.base.getExpertCount(k)

            spn.SetValue(cur)
            spn.SetMin(lower)
            spn.SetMax(upper)

        self.view.choiceCogc.Clear()
        self.view.choiceCogc.Append(self.base.planet.cogcType() or "NONE")
        self.view.choiceCogc.Select(0)
        self.view.choiceCogc.Disable()

    def reloadBuildingsFromModel(self):
        productionBuildingControllerTickers = set()
        for c in self.productionBuildingControllers:
            c.reloadViewFromModel()
            productionBuildingControllerTickers.add(c.ticker)

        for k in self.base.buildings:
            if k not in productionBuildingControllerTickers \
                and k not in models.empire.infrastructureBuildingTickers \
                and len(self.base.recipesForBuilding(k)) > 0:
                self.productionBuildingControllers.append(ProductionBuildingController(self, self.base, k))

        for c in self.productionBuildingControllers[:]:
            if c.ticker not in self.base.buildings:
                c.onClose()
                self.productionBuildingControllers.remove(c)

        self.availableBuildings = []
        self.availableBuildingLabels = []
        for k, bui in models.prun.buildings.items():
            if bui.Ticker not in productionBuildingControllerTickers and \
                bui.Ticker not in self.availableBuildings and \
                len(self.base.recipeIdsForBuilding(bui.Ticker)) > 0 and \
                self.base.getLimitsForBuilding(bui.Ticker)[1] > 0 and \
                self.base.getBuildingCount(bui.Ticker) == 0:
                self.availableBuildings.append(bui.Ticker)
                self.availableBuildingLabels.append(f"[{bui.Ticker}] {bui.Name}")

        self.availableBuildings.sort()
        self.availableBuildingLabels.sort()

        self.view.choiceNewBuilding.Set(self.availableBuildingLabels)
        self.view.buttonAddBuilding.Enabled = (self.view.choiceNewBuilding.Selection != wx.NOT_FOUND)

    def reloadShoppingListFromModel(self):
        self.view.radioBoxCargoBay.SetSelection(self.base.defaultShipTypeIdx)

        self.view.listCtrlShopping.ClearAll()

        self.view.listCtrlShopping.AppendColumn("Ticker")
        self.view.listCtrlShopping.AppendColumn("Count")
        self.view.listCtrlShopping.AppendColumn("t")
        self.view.listCtrlShopping.AppendColumn('m3')

        total_t = 0
        total_m3 = 0
        total_days = 0

        otherBase = self.app.compareEmpire.getBaseForPlanet(self.base.planet.PlanetNaturalId)
        buildingDiff = self.base.getBuildingDeltaFromOtherBase(otherBase)
        if len(buildingDiff):
            self.view.listCtrlShopping.Append(("Buildings",))
            for k, v in buildingDiff.items():
                self.view.listCtrlShopping.Append((k, v))

            constructionBill = self.base.getConstructionShoppingListVsOtherBase(otherBase)
            if len(constructionBill):
                self.view.listCtrlShopping.Append(("Con. Mats",))
                sorted_constructionBill = [i for i in constructionBill.items()]
                sorted_constructionBill.sort(key=lambda x: models.prun.materials[x[0]].CategoryName + " " + models.prun.materials[x[0]].Name)

                for k, v in sorted_constructionBill:
                    mat = models.prun.materials[k]
                    dwgt = mat.Weight * v
                    dvol = mat.Volume * v
                    self.view.listCtrlShopping.Append((k, v, round(dwgt, 2), round(dvol, 2)))
                    total_t += dwgt
                    total_m3 += dvol

        inFlows = {k: v for k, v in dict_mul(self.base.getDailyMaterialFlow(), -1).items() if v > 0}
        if len(inFlows):
            self.view.listCtrlShopping.Append(("Supply",))
            capacity_t, capacity_m3 = models.empire.shipCapacities[self.view.radioBoxCargoBay.Selection]
            remaining_t = capacity_t - total_t
            remaining_m3 = capacity_m3 - total_m3

            total_list, total_days = self.base.getSupplyListAndDuration(remaining_t, remaining_m3)

            sorted_totalList = [i for i in total_list.items()]
            sorted_totalList.sort(key=lambda x: models.prun.materials[x[0]].CategoryName + " " + models.prun.materials[x[0]].Name)

            for k, v in sorted_totalList:
                mat = models.prun.materials[k]
                dwgt = mat.Weight * v
                dvol = mat.Volume * v
                self.view.listCtrlShopping.Append((k, v, round(dwgt, 2), round(dvol, 2)))
                total_t += dwgt
                total_m3 += dvol

        if total_t > 0 or total_m3 > 0:
            self.view.listCtrlShopping.Append(("Total t/m3", "", round(total_t, 2), round(total_m3, 2)))
        if total_days > 0:
            self.view.listCtrlShopping.Append(("Total d", round(total_days, 2)))

    def reloadSummaryViewFromModel(self):
        self.view.radioBoxCargoBay.SetSelection(self.base.defaultShipTypeIdx)

        self.view.listCtrlSummary.ClearAll()

        self.view.listCtrlSummary.AppendColumn("")
        self.view.listCtrlSummary.AppendColumn("")
        self.view.listCtrlSummary.AppendColumn("")
        self.view.listCtrlSummary.AppendColumn("")

        daily_flow = self.base.getDailyMaterialFlow()
        daily_in = {k: v for k, v in dict_mul(daily_flow, -1).items() if v > 0}
        daily_out = {k: v for k, v in dict_mul(daily_flow, 1).items() if v > 0}

        cost_in = models.prun.purchaseCostForBasket(daily_in)
        m3_in, t_in = models.prun.sizesPerBasket(daily_in)

        revenue_out = models.prun.saleRevenueForBasket(daily_out)
        m3_out, t_out = models.prun.sizesPerBasket(daily_out)

        capacity_t, capacity_m3 = models.empire.shipCapacities[self.view.radioBoxCargoBay.Selection]

        self.view.listCtrlSummary.Append(("Totals", "¤", "t", "m3"))
        self.view.listCtrlSummary.Append(("In", int(cost_in), round(t_in, 2), round(m3_in, 2)))
        self.view.listCtrlSummary.Append(("Out", int(revenue_out), round(t_out, 2), round(m3_out, 2)))
        self.view.listCtrlSummary.Append(("",))

        if m3_in > 0 or t_in > 0:
            total_days_in = min(capacity_t / t_in, capacity_m3 / m3_in)
            self.view.listCtrlSummary.Append(("Imp. d", round(total_days_in, 2)))
        if m3_out > 0 or t_out > 0:
            total_days_out = min(capacity_t / t_out, capacity_m3 / m3_out)
            self.view.listCtrlSummary.Append(("Exp. d", round(total_days_out, 2)))
        self.view.listCtrlSummary.Append(("",))

        self.view.listCtrlSummary.Append(("Finance",))
        capitalCost = self.base.getTotalCapitalCost()
        startupCost = self.base.getTotalStartupCost(capacity_t, capacity_m3)
        self.view.listCtrlSummary.Append(("Capital Cost", int(capitalCost)))
        self.view.listCtrlSummary.Append(("Startup Cost", int(startupCost)))

        weeklyProfit = self.base.getExpectedDailyProfit() * 7
        self.view.listCtrlSummary.Append(("Weekly Profit", int(weeklyProfit)))
        self.view.listCtrlSummary.Append(("Weekly Pft %", "{0}%".format(round(weeklyProfit * 100 / startupCost, 2))))

        maximumInterestCharge = float(models.prun.config['Config']['WeeklyInterestRate']) * startupCost
        minimumPrincipalRepaymentAmt = weeklyProfit - maximumInterestCharge
        if minimumPrincipalRepaymentAmt <= 0:
            self.view.listCtrlSummary.Append(("Payoff (wk)", "∞"))
        else:
            self.view.listCtrlSummary.Append(("Payoff (wk)", math.ceil(startupCost / minimumPrincipalRepaymentAmt)))

        self.view.listCtrlSummary.Append(("",))

        if self.app.compareEmpire:
            e2: models.empire.Empire = self.app.compareEmpire
            b2 = e2.getBaseForPlanet(self.base.planet.PlanetNaturalId)
            if b2:
                deltaCapCost = int(self.base.getDeltaCapitalCost(b2))
                if deltaCapCost != 0:
                    self.view.listCtrlSummary.Append(("Expansion",))
                    self.view.listCtrlSummary.Append(("Δ Cap. Cost", deltaCapCost))
                    deltaWeeklyProfit = self.base.getExpectedDailyProfitChange(b2) * 7
                    self.view.listCtrlSummary.Append(("Δ Wk. Pft", int(deltaWeeklyProfit)))
                    self.view.listCtrlSummary.Append(("Δ Pft %", "{0}%".format(round(deltaWeeklyProfit * 100 / deltaCapCost, 2))))

                    maximumInterestCharge = float(models.prun.config['Config']['WeeklyInterestRate']) * deltaCapCost
                    minimumPrincipalRepaymentAmt = deltaWeeklyProfit - maximumInterestCharge
                    if minimumPrincipalRepaymentAmt <= 0:
                        self.view.listCtrlSummary.Append(("Payoff (wk)", "∞"))
                    else:
                        self.view.listCtrlSummary.Append(("Payoff (wk)", math.ceil(deltaCapCost / minimumPrincipalRepaymentAmt)))

        for i in range(self.view.listCtrlSummary.ColumnCount):
            self.view.listCtrlSummary.SetColumnWidth(i, wx.LIST_AUTOSIZE)



    def reloadViewFromModel(self):
        self.view.labelBaseName.SetLabel(self.base.planet.PlanetName)
        self.view.SetTitle(self.base.planet.PlanetName)
        self.view.labelArea.SetLabel(f"Area: {self.base.getTotalArea()} ({self.base.getPermits()})")

        self.view.checkBoxCompanyHQ.Value = self.base.isCompanyHQ
        self.view.checkBoxCorpHQ.Value = self.base.isCorpHQ

        self.reloadResourcesFromModel()
        self.reloadMaterialFlowsFromModel()
        self.reloadWorkerStatisticsFromModel()
        self.reloadSpinnersFromModel()
        self.reloadBuildingsFromModel()
        self.reloadShoppingListFromModel()
        self.reloadSummaryViewFromModel()



class ProductionBuildingController(controllers.controller.Controller):
    def __init__(self, parent, base, ticker, *args, **kw):
        super().__init__(parent, base, ticker, *args, **kw)

        self.parentController : BaseController = parent
        self.base : models.empire.Base = base
        self.view = resources.gui.ProductionBuildingPanel(self.parentController.view.scrolledWindowProduction)
        self.ticker: str = ticker

        self.availableRecipeIds = []

        self.view.spinCtrlCount.Bind(wx.EVT_SPINCTRL, self.onSpinCtrlUpdated)
        self.view.buttonAddRecipe.Bind(wx.EVT_BUTTON, self.onAddRecipe)
        self.view.buttonRemove.Bind(wx.EVT_BUTTON, self.onRemoveButtonClicked)

        self.recipeControllers : list[ProductionBuildingRecipeController] = []

        self.reloadViewFromModel()
        sz : wx.Sizer = self.parentController.view.scrolledWindowProduction.GetSizer()
        sz.Add(self.view, 0, wx.EXPAND)
        self.view.Show()

        self.parentController.view.Layout()
        # sz.FitInside(self.parentController.view.scrolledWindowProduction)

    def onClose(self):
        for c in self.recipeControllers:
            c.onClose()
        self.recipeControllers.clear()
        self.view.DestroyLater()
        self.parentController.view.Layout()

    def onAddRecipe(self, event: wx.CommandEvent):
        if len(self.availableRecipeIds) > 0:
            i = self.view.choiceAddRecipe.Selection
            if i != wx.NOT_FOUND and i < len(self.availableRecipeIds):
                recipeId = self.availableRecipeIds[i]
                self.base.setRecipeQty(recipeId, 1)

    def onRemoveButtonClicked(self, event: wx.CommandEvent):
        self.base.removeBuilding(self.ticker)

    def reloadViewFromModel(self):
        self.view.labelTicker.Label = self.ticker
        self.view.spinCtrlCount.Value = self.base.getBuildingCount(self.ticker)
        lower, upper = self.base.getLimitsForBuilding(self.ticker)
        self.view.spinCtrlCount.Min = lower
        self.view.spinCtrlCount.Max = upper

        if self.parentController.app.compareEmpire:
            e : models.empire.Empire = self.parentController.app.compareEmpire
            if self.base.planet.PlanetNaturalId in e.basesMap:
                b2 : models.empire.Base = e.basesMap[self.base.planet.PlanetNaturalId]
                delta = self.base.getBuildingCount(self.ticker) - b2.getBuildingCount(self.ticker)

                self.view.labelCountDelta.Label = f"Δ: {delta:+}"


        activeRecipeIds = set()
        for c in self.recipeControllers:
            c.reloadViewFromModel()
            activeRecipeIds.add(c.recipeId)

        baseRecipeIds = set()
        for recipeId in self.base.activeRecipeIdsForBuilding(self.ticker):
            baseRecipeIds.add(recipeId)
            if recipeId not in activeRecipeIds:
                ct = ProductionBuildingRecipeController(self, self.base, recipeId)
                self.recipeControllers.append(ct)

        recipeIdsToRemove = activeRecipeIds.difference(baseRecipeIds)
        for c in self.recipeControllers[:]:
            if c.recipeId in recipeIdsToRemove:
                c.onClose()
                self.recipeControllers.remove(c)

        self.availableRecipeIds = []
        for r in self.base.recipeIdsForBuilding(self.ticker):
            if r not in baseRecipeIds:
                self.availableRecipeIds.append(r)
        self.view.choiceAddRecipe.Set([f"({self.base.getRecipeProfitEstimate(id):7.0f}) {id}" for id in self.availableRecipeIds])


    def onSpinCtrlUpdated(self, event: wx.SpinEvent):
        self.base.setBuildingCount(self.ticker, event.Position)

class ProductionBuildingRecipeController(controllers.controller.Controller):
    def __init__(self, parent, base, recipeId, *args, **kw):
        super().__init__(parent, base, recipeId, *args, **kw)

        self.parentController : ProductionBuildingController = parent
        self.base : models.empire.Base = base
        self.recipeId : str = recipeId
        self.view = resources.gui.ProductionBuildingRecipePanel(self.parentController.view.panelRecipes)

        self.view.spinCtrlCount.Bind(wx.EVT_SPINCTRL, self.onSpinCtrlUpdated)
        self.view.buttonRemove.Bind(wx.EVT_BUTTON, self.onRemoveButton)

        self.reloadViewFromModel()

        sz : wx.Sizer = self.parentController.view.panelRecipes.GetSizer()
        szCount = sz.ItemCount
        sz.Insert(szCount - 1, self.view, flag=wx.ALL, border=5)
        self.view.Show()
        self.parentController.parentController.view.Layout()

    def onClose(self):
        self.view.DestroyLater()
        self.parentController.parentController.view.Layout()

    def onSpinCtrlUpdated(self, event: wx.SpinEvent):
        self.base.setRecipeQty(self.recipeId, event.Position)

    def onRemoveButton(self, event: wx.CommandEvent):
        self.base.removeRecipe(self.recipeId)

    def reloadViewFromModel(self):
        self.view.labelRecipe.Label = self.recipeId
        self.view.labelEstimatedProfit.Label = f"COGM: {self.base.getRecipeCogmNumeric(self.recipeId):7.2f}\nEst. Pf: {self.base.getRecipeProfitEstimate(self.recipeId):7.0f}"
        self.view.spinCtrlCount.Value = self.base.getRecipeQty(self.recipeId)