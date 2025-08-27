import os
from .startConsole import startConsole
from .initFuncsCall import getInitForAllTabs
ABS_PATH = os.path.abspath(__file__)
ABS_DIR = os.path.dirname(ABS_PATH)
getInitForAllTabs(ABS_DIR)
from .windowManagerConsole import windowManagerConsole,startWindowManagerConsole
from .appRunnerTab import appRunnerTab,startAppRunnerConsole
from .launcherWindowTab import launcherWindowTab,startLauncherWindowConsole
from .logPaneTab import logPaneTab,startLogPaneTabConsole

