import sys
import os
import platform
import importlib.util
import subprocess
import glob
import shutil
import pkg_resources



def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources
   so_file = os.path.join(os.path.dirname(__file__),f"IOSimulator.so")
   spec = importlib.util.spec_from_file_location("IOSimulator", so_file)
   mylib = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(mylib)
   sys.modules[__name__] = mylib

# Then, load the shared library
__bootstrap__()
