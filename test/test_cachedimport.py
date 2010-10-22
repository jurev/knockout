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



CACHE_DIR = "_testenv"

if "reset" in sys.argv:
    reset_testenv(CACHE_DIR)
    print "RESET"
    sys.exit()


#reset_testenv(CACHE_DIR)

from knockout import urlimport, cachedimport
urlimport.clear_cache()

cachedimport.FileCacheImporter.CACHE_DIR = CACHE_DIR
cachedimport.FileCacheImporter.register()

sys.path.insert(-1, "http://127.0.0.1:8000/#colors")

# success
import colors.blue

# fail
#import danger.woot

#sys.path.insert(-1, "http://127.0.0.1:8000/#colors")

# success
#import danger.woot
