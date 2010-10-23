import cachedimport, urlimport
import logging
logging.basicConfig(level=urlimport.SOURCE)
log = logging.getLogger("gaeimport")

import os2 as os
import __builtin__

class FileCacheImporter(cachedimport.FileCacheImporter):    
    def get_cached_source(self, localpath):
        """Get the cached source for the given url.
        """
        localpath = os.path.abspath(localpath)
        log.debug("get_source: this is my localpath: %s" % localpath)        
        try:
            log.debug("get_source: trying to get %s from cache" % localpath)        
            return __builtin__.open(localpath).read()
        except:
            pass
        raise cachedimport.NotInCacheException("Not in cache: %s" % localpath)

    def make_symlink(self, src, dst):
        src = os.path.abspath(src)
        if src.endswith(".py") and not dst.endswith(".py"):
             dst = os.path.join(dst, os.path.basename(src))
        if src.endswith("/__init__.py"):
            src = os.path.dirname(src)
            dst = os.path.join(os.path.dirname(dst), os.path.basename(src)) 
        try:
            if src and dst:
                try:
                    os.remove(dst)
                except:
                    pass
                os.symlink(src, dst)
        except:
            log.exception("make_symlink")
        
    def put_source(self, localpath, source):
        """Put the source obtained from the given url to cache.
        
           Use a custom makedirs() to overcome dev_appserver restrictions.
        """
        localpath = os.path.abspath(localpath)
        dirname = os.path.dirname(localpath)
        log.debug("put_source: trying to create %s" % dirname)
        try:
            os.makedirs(dirname)
        except:
            pass
        log.debug("put_source: trying to write %s" % localpath)
        __builtin__.open(localpath, "w").write(source)
        log.debug("put_source: wrote %s" % localpath)
