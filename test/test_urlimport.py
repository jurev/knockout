import os, sys
import shutil

sys.path.insert(0, ".")
import knockout

def _j(*args):
    return os.path.join(*args)

def reset_testenv(target):
    for x in os.listdir(target):
        f = _j(target, x)
        if os.path.isdir(f):
            shutil.rmtree(f)


reset_testenv("_testenv")

from knockout import urlimport
urlimport.clear_cache()

sys.path.insert(-1, "http://127.0.0.1:8000/#colors")

# success
import colors.blue

# fail
import danger.woot

sys.path.insert(-1, "http://127.0.0.1:8000/#colors")

# success
import danger.woot
