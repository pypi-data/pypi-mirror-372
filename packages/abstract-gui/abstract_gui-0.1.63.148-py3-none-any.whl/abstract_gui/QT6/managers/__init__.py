import os
from abstract_utilities.dynimport import import_symbols_to_parent
import_modules = [
    {"module":'abstract_gui',"symbols":['get_for_all_tabs','startConsole']}
     ]
import_symbols_to_parent(import_modules, update_all=True)
get_for_all_tabs()
from .windowManagerConsole import windowManagerConsole,startWindowManagerConsole
from .appRunnerTab import appRunnerTab,startAppRunnerConsole
from .launcherWindowTab import launcherWindowTab,startLauncherWindowConsole
from .logPaneTab import logPaneTab,startLogPaneTabConsole

