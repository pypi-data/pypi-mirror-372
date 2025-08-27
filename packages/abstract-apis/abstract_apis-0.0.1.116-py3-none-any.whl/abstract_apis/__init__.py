import os
from abstract_utilities.dynimport import import_symbols_to_parent
import_modules = [
    {"module":'abstract_utilities',"symbols":['call_for_all_tabs']}
     ]
import_symbols_to_parent(import_modules, update_all=True)
call_for_all_tabs()
from .make_request import *
from .async_make_request import *
from .apiTab import startApiConsole,apiTab
