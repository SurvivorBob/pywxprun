import wx
import pubsub.pub

import resources.gui
import models.empire
import models.prun

import controllers.controller
import controllers.base

import logging

class PlanetSearchController(controllers.controller.Controller):
    def __init__(self, app, empire):
        super().__init__(app, empire)

        self.app = app
        self.empire : models.empire.Empire = empire
        self.view : resources.gui.PlanetSearchView = resources.gui.PlanetSearchView(None)

        self.searchResults : list[models.prun.Planet] = []

        self.app.RegisterController(self)

        self.view.Bind(wx.EVT_CLOSE, self.onClose)
        self.view.buttonSearch.Bind(wx.EVT_BUTTON, self.onDoSearch)
        self.view.buttonCreate.Bind(wx.EVT_BUTTON, self.onDoCreate)
        self.view.listCtrlResults.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoCreate)

        self.view.Show()

    def onClose(self, _):
        self.app.UnregisterController(self)
        self.view.Destroy()

    def onDoSearch(self, event):
        planets = models.prun.planet_search(self.view.textCtrlSearch.Value)
        planets_ordered = [[p, None, 0, 0, 0, 0] for p in planets if p.PlanetNaturalId not in self.empire.basesMap]

        sys_ai1 = models.prun.systems_trie.search("ZV-307")[0]
        sys_ci1 = models.prun.systems_trie.search("UV-351")[0]
        sys_ic1 = models.prun.systems_trie.search("VH-331")[0]
        sys_nc1 = models.prun.systems_trie.search("OT-580")[0]

        for z in planets_ordered:
            st = models.prun.systems[z[0].SystemId]
            z[2] = st.connectedDistanceTo(sys_ai1)
            z[3] = st.connectedDistanceTo(sys_ci1)
            z[4] = st.connectedDistanceTo(sys_ic1)
            z[5] = st.connectedDistanceTo(sys_nc1)

        dist_from_str = self.view.textCtrlDistFrom.Value
        test_star: models.prun.StarSystem = None
        if len(dist_from_str) > 0:
            test_stars = models.prun.systems_trie.search(dist_from_str)
            if len(test_stars):
                test_star = test_stars[0]
                for z in planets_ordered:
                    z[1] = models.prun.systems[z[0].SystemId].connectedDistanceTo(test_star)
                planets_ordered.sort(key=lambda z: z[1])

        if len(self.view.textCtrlResourceFilter.Value) > 0:
            def resource_predicate(p: models.prun.Planet) -> bool:
                return any((self.view.textCtrlResourceFilter.Value in k) for k in p.DailyResourcesSummary)
            planets_ordered = [z for z in planets_ordered if resource_predicate(z[0])]

        if len(self.view.textCtrlCOGCFilter.Value) > 0:
            planets_ordered = [z for z in planets_ordered if self.view.textCtrlCOGCFilter.Value in str(z[0].cogcType())]

        self.searchResults = [z[0] for z in planets_ordered]

        ct = self.view.listCtrlResults
        ct.ClearAll()
        ct.InsertColumn(0, "Planet")
        if test_star:
            ct.InsertColumn(1, f"Dist. {test_star.NaturalId}")
        ct.InsertColumn(2, "COGC")
        ct.InsertColumn(3, "Mats")
        ct.InsertColumn(4, "Res/Area")

        ct.InsertColumn(5, "AI1")
        ct.InsertColumn(6, "CI1")
        ct.InsertColumn(7, "IC1")
        ct.InsertColumn(8, "NC1")

        for z in planets_ordered:
            planet : models.prun.Planet = z[0]
            dist : float = z[1]
            row = []
            row.append(planet.PlanetName)
            if test_star:
                row.append(f"{dist:.1f}")
            row.append(planet.cogcType())

            mat_str = " ".join(sorted((m for m in planet.buildingMaterials()), key=models.prun.buildingMaterialSortOrder))
            row.append(mat_str)

            res_summary = sorted(((k, v) for k, v in planet.dailyResourcesPerArea().items()), key=lambda z: z[1], reverse=True)
            res_str = ", ".join(f"{v:.2f} {k}" for k, v in res_summary)
            row.append(res_str)

            row.append(f"{z[2]:.1f}")
            row.append(f"{z[3]:.1f}")
            row.append(f"{z[4]:.1f}")
            row.append(f"{z[5]:.1f}")

            ct.Append(row)

        for i in range(ct.ColumnCount):
            ct.SetColumnWidth(i, wx.LIST_AUTOSIZE)

    def onDoCreate(self, event):
        self.tryCreateBase()

    def onItemDoubleClicked(self, event):
        self.tryCreateBase()

    def tryCreateBase(self):
        which_planet = self.view.listCtrlResults.GetNextSelected(-1)
        if which_planet != -1:
            p = self.searchResults[which_planet]
            logging.info(p.PlanetName)

            b = self.empire.createBase(p.PlanetNaturalId)
            if b:
                c = controllers.base.BaseController(self.app, b)
                self.view.Close()
