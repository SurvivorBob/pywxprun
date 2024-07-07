import wx

import models.prun

import models.empire
import controllers.splash
import controllers.controller
import controllers.empire
import controllers.base

import threading

import logging
import traceback
import json

class MainApp(wx.App):
    def __init__(self, *args, **kw):
        self.controllers = set()

        self.e : models.empire.Empire | None = None
        self.compareEmpire : models.empire.Empire | None = None

        super().__init__(*args, **kw)

    def RegisterController(self, c: controllers.controller.Controller):
        self.controllers.add(c)
        c.onRegister()

        return c

    def UnregisterController(self, c: controllers.controller.Controller):
        if c in self.controllers:
            self.controllers.remove(c)
            c.onUnregister()

    def OnInit(self):
        self.e = models.empire.Empire()

        self._splash_controller = self.RegisterController(controllers.splash.SplashController(self))
        self._load_thread = threading.Thread(target=self.DoLoad)

        self._load_thread.start()

        return True

    def DoLoad(self):
        models.prun.reload_all()

        wx.CallAfter(self.OnLoadComplete)

    def OnLoadComplete(self):
        self.RegisterController(controllers.empire.EmpireController(self, self.e))
        self.UnregisterController(self._splash_controller)

        try:
            self.LoadFromFile("default.json")
            logging.info("loaded empire from file")
        except OSError as e:
            logging.warn(traceback.format_exception(e))
            logging.info("default.json inaccessible or not found, loading empire from FIO")
            self.LoadFromFIO()

        return True

    def LoadFromFile(self, fn):
        for c in self.controllers:
            if type(c) is controllers.base.BaseController:
                c.view.Close()
        with open(fn, "r") as f:
            d = json.load(f)
            e = models.empire.Empire.unserialize(d)
            e2 = models.empire.Empire.loadFromFIO()

            if e2:
                e2_bases = {b.planet.PlanetNaturalId: b for b in e2.bases}
                for b in e.bases:
                    if b.planet.PlanetNaturalId in e2_bases:
                        b2 = e2_bases[b.planet.PlanetNaturalId]

                        b.SiteId = b2.SiteId

                        for k, v in b.experts.items():
                            b2.experts[k] = v
                        b2.setIsCompanyHQ(b.isCompanyHQ)
                        b2.setIsCorpHQ(b.isCorpHQ)

            self.e = e
            self.compareEmpire = e2 or models.empire.Empire.unserialize(e.serialize())
            for c in self.controllers:
                if type(c) is controllers.empire.EmpireController:
                    c.switchEmpire(self.e)
                    c.setCompareEmpire(self.compareEmpire)

    def LoadFromFIO(self):
        for c in self.controllers:
            if type(c) is controllers.base.BaseController:
                c.view.Close()
        e = models.empire.Empire.loadFromFIO()

        if not e:
            logging.info("can't load an empire from FIO, creating an example empire")
            e = models.empire.Empire()
            b = e.createBase("VH-331a")
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

        e2 = models.empire.Empire.unserialize(e.serialize())
        self.e = e
        self.compareEmpire = e2
        for c in self.controllers:
            if type(c) is controllers.empire.EmpireController:
                c.switchEmpire(self.e)
                c.setCompareEmpire(self.compareEmpire)

    def SaveToFile(self, fn):
        d = self.e.serialize()
        with open(fn, "w") as f:
            json.dump(d, f)