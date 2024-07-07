from __future__ import annotations

import wx
import pubsub.pub   

import models.app

import controllers.controller

import resources.gui

import logging

class SplashController(controllers.controller.Controller):
    def __init__(self, app: models.app.MainApp):
        super().__init__(app)

        self.app: models.app.MainApp = app
        self.view: resources.gui.SplashFrame = resources.gui.SplashFrame(None)

        self.app.RegisterController(self)
        self.view.Show()

    def onUnregister(self, *args, **kw):
        self.view.Destroy()
        return super().onUnregister(*args, **kw)