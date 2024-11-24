import wx
import pubsub.pub

import controllers.controller
import controllers.planet_search
import models.prun
import resources.gui
import models.empire
import controllers.base

import logging
import math

import threading

class EmpireController(controllers.controller.Controller):
    def __init__(self, app, empire, *args, **kw):
        super().__init__(app, empire, *args, **kw)
        self.app = app
        self.empire : models.empire.Empire = empire
        self.compareEmpire : models.empire.Empire | None = None
        self.view : resources.gui.EmpireView = resources.gui.EmpireView(None)
        self.acceptingUpdates = True

        self._updateThread = None

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

        self.view.toolBar.Bind(wx.EVT_TOOL, self.onRefreshClicked, id=self.view.toolRefreshFio.GetId())

        self.view.toolBar.EnableTool(self.view.toolNewEmpire.GetId(), False)
        self.view.toolBar.EnableTool(self.view.toolLoadEmpire.GetId(), False)
        self.view.toolBar.EnableTool(self.view.toolSaveEmpire.GetId(), False)

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

            if self.compareEmpire and self.compareEmpire.getBaseForPlanet(b.planet.PlanetNaturalId) and self.compareEmpire.getBaseForPlanet(b.planet.PlanetNaturalId)._needsRepair:
                name_str = "🛠️ " + name_str

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
            i_or_e = "I"
            exports_list = b.getAvailableExports()
            total_t, total_m3 = 0, 0
            for k, v in exports_list.items():
                mat = models.prun.materials[k]
                dwgt = mat.Weight * v
                dvol = mat.Volume * v
                total_t += dwgt
                total_m3 += dvol
            exports_fill = round(max(total_t / capacity_t, total_m3 / capacity_m3) * 100)
            if exports_fill > percent_ship_fill:
                percent_ship_fill = exports_fill
                i_or_e = "E"

            self.view.basesList.Append([
                name_str,
                b.getTotalArea(),
                b.getPermits(),
                f"{round(b.getCurrentSupplyDays(), 1)}",
                f"{percent_ship_fill} {i_or_e}"
            ])
            self.basesListed.append(b)

        for i in range(self.view.basesList.ColumnCount):
            self.view.basesList.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

        self.reloadFlows()
        self.refreshDeleteBaseButton()

        inventorySurplusesByHub = self.empire.getInventorySurplusesByHub()
        flowsByHub = self.empire.getMaterialFlowsByHub()
        hubs = [k for k in inventorySurplusesByHub.keys()]
        items = set()
        for h in hubs:
            items = items.union((k for k in inventorySurplusesByHub[h]))

        # lol wut
        if None in items:
            items.remove(None)

        items = list(items)
        logging.info(items)
        items.sort(key=lambda x: models.prun.materials[x].CategoryName + " " + models.prun.materials[x].Name)

        self.view.shoppingCartList.ClearAll()
        self.view.shoppingCartList.InsertColumn(0, "Mat")
        for i, h in enumerate(hubs):
            self.view.shoppingCartList.InsertColumn(1 + i, h)

        for m in items:
            r = [m] + [f"{math.floor(inventorySurplusesByHub[h].get(m, 0))} {'+' if flowsByHub[h].get(m, 0) > 0 else '-' if flowsByHub[h].get(m, 0) < 0 else ''}" for h in hubs]
            self.view.shoppingCartList.Append(r)

    def onRefreshClicked(self, event):
        self.view.statusBar.PushStatusText("refreshing")
        self.view.toolBar.EnableTool(self.view.toolRefreshFio.GetId(), False)

        self._updateThread = threading.Thread(target=self.doRefreshFio)
        self._updateThread.start()

    def doRefreshFio(self):
        models.prun.reload_live_data(0)
        wx.CallAfter(self.onRefreshComplete)

    def onRefreshComplete(self):
        e2 = models.empire.Empire.loadFromFIO()

        if e2:
            e2_bases = {b.planet.PlanetNaturalId: b for b in e2.bases}
            for b in self.empire.bases:
                if b.planet.PlanetNaturalId in e2_bases:
                    b2 = e2_bases[b.planet.PlanetNaturalId]

                    b.SiteId = b2.SiteId

                    for k, v in b.experts.items():
                        b2.experts[k] = v
                    b2.setIsCompanyHQ(b.isCompanyHQ)
                    b2.setIsCorpHQ(b.isCorpHQ)
            self.setCompareEmpire(e2)

        self.onEmpireChanged(id(self.empire))
        self.view.statusBar.PopStatusText()
        self.view.toolBar.EnableTool(self.view.toolRefreshFio.GetId(), True)

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
