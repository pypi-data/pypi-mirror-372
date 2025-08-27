from abstract_utilities.dynimport import import_symbols_to_parent
import_modules = [
    {"module":'abstract_utilities',"symbols":['call_for_all_tabs']}
     ]
import_symbols_to_parent(import_modules, update_all=True)
call_for_all_tabs()
from .apiTab import startApiConsole,apiTab
