import wx
import pubsub.pub

import controllers.controller
import controllers.planet_search
import resources.gui
import models.empire
import controllers.base

import logging

class EmpireController(controllers.controller.Controller):
    def __init__(self, app, empire, *args, **kw):
        super().__init__(app, empire, *args, **kw)
        self.app = app
        self.empire : models.empire.Empire = empire
        self.compareEmpire : models.empire.Empire | None = None
        self.view : resources.gui.EmpireView = resources.gui.EmpireView(None)
        self.acceptingUpdates = True

        self.basesListed = []

        self.app.RegisterController(self)

        self.view.Bind(wx.EVT_CLOSE, self.onClose)
        self.view.buttonCreateBase.Bind(wx.EVT_BUTTON, self.onCreateBaseClicked)
        self.view.buttonEditBase.Bind(wx.EVT_BUTTON, self.onEditBaseClicked)
        self.view.buttonDeleteBase.Bind(wx.EVT_BUTTON, self.onDeleteBaseClicked)
        self.view.basesList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onBaseSelected)
        self.view.basesList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onBaseSelected)
        self.view.basesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onBaseDoubleClicked)
        self.view.textCtrlFlowsFilter.Bind(wx.EVT_TEXT, self.onFlowsFilterChanged)
        self.view.checkBoxBalance.Bind(wx.EVT_CHECKBOX, self.onBalanceToggled)

        self.reloadViewFromModel()

        pubsub.pub.subscribe(self.onEmpireChanged, "empire_changed")
        pubsub.pub.subscribe(self.onWindowForBaseClosed, "base_window_closed")
        self.view.Show()

    def onClose(self, event):
        self.app.SaveToFile("saved.json")
        wx.Exit()

    def switchEmpire(self, new_empire):
        self.empire = new_empire
        self.onEmpireChanged(id(self.empire))

    def setCompareEmpire(self, new_empire):
        self.compareEmpire = new_empire
        self.onEmpireChanged(id(self.empire))

    def onEmpireChanged(self, empire_id):
        if empire_id == id(self.empire) and self.acceptingUpdates:
            self.acceptingUpdates = False
            self.reloadViewFromModel()
            self.app.SaveToFile("default.json")
            self.acceptingUpdates = True

    def onBalanceToggled(self, event):
        self.reloadViewFromModel()

    def onFlowsFilterChanged(self, event):
        self.reloadFlows()

    def reloadFlows(self):
        self.view.flowsList.ClearAll()

        self.view.flowsList.InsertColumn(0, "Mat")
        self.view.flowsList.InsertColumn(1, "Amt/d")
        self.view.flowsList.InsertColumn(2, "Rev/d")

        totalEmpireFlow = self.empire.getTotalMaterialFlow()
        allProduced = set()
        allConsumed = set()
        if self.view.checkBoxBalance.Value:
            for b in self.empire.bases:
                for k, v in b.getDailyMaterialInFlow().items():
                    if v < 0:
                        allConsumed.add(k)
                for k, v in b.getDailyMaterialOutFlow().items():
                    if v > 0:
                        allProduced.add(k)
            toShow = allProduced.intersection(allConsumed)
            flows_list = [
                (k,
                round(v, 2),
                int(self.empire.getProfitForSingleMaterialFlow(k, v)))
                for k, v in totalEmpireFlow.items()
                if k in toShow
            ]
            flows_list.sort(key=lambda x: x[2], reverse=True)

        else:
            flows_list = [
                (k,
                round(v, 2),
                int(self.empire.getProfitForSingleMaterialFlow(k, v)))
                for k, v in totalEmpireFlow.items()
            ]
            flows_list.sort(key=lambda x: x[2], reverse=True)

            total_profit = sum(n[2] for n in flows_list if n is not None)
            self.view.flowsList.Append(("Total", "", int(total_profit)))

        if self.view.textCtrlFlowsFilter.Value:
            filterValues = str(self.view.textCtrlFlowsFilter.Value).split(" ")
            flows_list = [x for x in flows_list if x[0] in filterValues]

        for x in flows_list:
            self.view.flowsList.Append(x)

        for i in range(self.view.flowsList.ColumnCount):
            self.view.flowsList.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

    def reloadViewFromModel(self):
        self.view.basesList.ClearAll()

        self.view.basesList.InsertColumn(0, "Planet")
        self.view.basesList.InsertColumn(1, "Area")
        self.view.basesList.InsertColumn(2, "Pmts")
        self.view.basesList.InsertColumn(3, "Brn (d)")
        self.view.basesList.InsertColumn(4, "% Ship")

        self.basesListed.clear()

        for b in self.empire.bases:
            name_str = b.planet.PlanetName
            if self.compareEmpire and len(b.getBuildingDeltaFromOtherBase(self.compareEmpire.getBaseForPlanet(b.planet.PlanetNaturalId))) > 0:
                name_str = "Δ " + name_str

            capacity_t, capacity_m3 = models.empire.shipCapacities[b.defaultShipTypeIdx]
            shopping_list, _ = b.getSupplyListAndDuration(float('inf'), float('inf'))
            total_t, total_m3 = 0, 0
            for k, v in shopping_list.items():
                mat = models.prun.materials[k]
                dwgt = mat.Weight * v
                dvol = mat.Volume * v
                total_t += dwgt
                total_m3 += dvol
            percent_ship_fill = round(max(total_t / capacity_t, total_m3 / capacity_m3) * 100)

            self.view.basesList.Append([
                name_str,
                b.getTotalArea(),
                b.getPermits(),
                round(b.getCurrentSupplyDays(), 1),
                percent_ship_fill
            ])
            self.basesListed.append(b)

        for i in range(self.view.basesList.ColumnCount):
            self.view.basesList.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

        self.reloadFlows()
        self.refreshDeleteBaseButton()

    def onCreateBaseClicked(self, event):
        c = controllers.planet_search.PlanetSearchController(self.app, self.empire)

    def onEditBaseClicked(self, event):
        which_base = self.view.basesList.GetNextSelected(-1)
        if which_base != -1:
            self.doOpenBase(which_base)

    def onDeleteBaseClicked(self, event):
        which_base = self.view.basesList.GetNextSelected(-1)
        if which_base != -1:
            b: models.empire.Base = self.basesListed[which_base]
            self.empire.deleteBase(b)

    def onBaseDoubleClicked(self, event: wx.ListEvent):
        self.doOpenBase(event.Index)

    def onWindowForBaseClosed(self, base_id):
        self.refreshDeleteBaseButton()

    def refreshDeleteBaseButton(self):
        which_base = self.view.basesList.GetNextSelected(-1)
        if which_base != -1:
            b: models.empire.Base = self.basesListed[which_base]
            for c in self.app.controllers:
                if type(c) == controllers.base.BaseController and c.base == b:
                    self.view.buttonDeleteBase.Disable()
                    return
            self.view.buttonDeleteBase.Enable()
        else:
            self.view.buttonDeleteBase.Disable()

    def onBaseSelected(self, event: wx.ListEvent):
        self.refreshDeleteBaseButton()

    def doOpenBase(self, which_base):
        b : models.empire.Base = self.basesListed[which_base]
        c = controllers.base.BaseController(self.app, b)
        self.refreshDeleteBaseButton()
