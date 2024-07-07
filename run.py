import models.prun
import models.app

import logging


if __name__ == "__main__":
    app = models.app.MainApp(False)

    app.MainLoop()