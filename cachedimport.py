import urlimport
import logging
logging.basicConfig(level=urlimport.SOURCE)
log = logging.getLogger("cachedimport")

import sys, os, re, shutil

class NotInCacheException(Exception):
    pass


class FileCacheImporter(urlimport.UrlImporter):
    """ Use filesystem storage as a cache.
    """

    CACHE_DIR = "./modules"
    SYMLINKS_DIR = None

    re_detailedpath = re.compile(''.join([
        r'^',
        r'(?P<protocol>http|ftp)',
        r'://',
        r'(?P<host>[^/]+)',        
        r'(?P<urlpath>.+)',
        r'$'
    ]))


    def find_module(self, fullname, mpath=None):
        """ Find module in the cache.
        """
        for url, path in self.get_candidates(fullname):
            try:
                localpath = self.translate_fullpath(url)
                self.source = self.get_cached_source(localpath)
            except Exception, e:
                log.debug("find_module: failed to get '%s'. (%s)" % (localpath, e))
            else:
                log.debug("find_module: got '%s'. mpath=%s" % (localpath, mpath))
                self.path = path
                self.__file__ = localpath
                if fullname == self.package:
                    self.make_symlink(self.__file__, self.SYMLINKS_DIR)
                return self

        result = super(FileCacheImporter, self).find_module(fullname, mpath)
        if result:
            self.put_source(self.translate_fullpath(result.__file__), result.source)
        return result    

    def make_symlink(self, src, dst):
        if src and dst:
            os.symlink(src, dst)

    def translate_fullpath(self, fullpath):
        """Get local path from fullpath.
        """
        translated = self.re_detailedpath.match(fullpath)
        if not translated:
            raise RuntimeError("translate_fullpath: Could not parse the given url: %s" % fullpath)
        root, folder, path = self.CACHE_DIR, translated.groupdict()["host"], translated.groupdict()["urlpath"][1:]
        localpath = '/'.join([root, folder, path])
        return localpath
    
    def get_cached_source(self, localpath):
        """Get the cached source for the given url.
        """
        log.debug("get_source: this is my localpath: %s" % localpath)        
        if os.path.isfile(localpath):
            log.debug("get_source: trying to get %s from cache" % localpath)        
            return open(localpath).read()
        raise NotInCacheException("Not in cache: %s" % localpath)
        
    def put_source(self, localpath, source):
        """Put the source obtained from the given url to cache.
        """
        dirname = os.path.dirname(localpath)
        log.debug("put_source: trying to create %s" % dirname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        log.debug("put_source: trying to write %s" % localpath)
        open(localpath, "w").write(source)
        log.debug("put_source: wrote %s" % localpath)        
    
    

class FunkyCacheImporter(urlimport.UrlImporter):
    """ Always store python files as packages(something/__init__.py)
    """
    
    CACHE_DIR = "./modules"

    re_detailedpath = re.compile(''.join([
        r'^',
        r'(?P<protocol>http|ftp)',
        r'://',
        r'(?P<host>[^/]+)',        
        r'(?P<urlpath>.+)',
        r'$'
    ]))


    def find_module(self, fullname, mpath=None):
        """ Find module in the cache.
        """
        for url, path in self.get_candidates(fullname):
            try:
                self.source = self.get_cached_source(url)
            except Exception, e:
                log.debug("find_module: failed to get '%s'. (%s)" % (url, e))
            else:
                log.debug("find_module: got '%s'. mpath=%s" % (url, mpath))
                self.path = path
                return self

        result = super(FileCacheImporter, self).find_module(fullname, mpath)
        if result:
            name = fullname.split(".")[-1]
            self.put_source(result.location + name + "/__init__.py", result.source)
        return result    

    def translate_fullpath(self, fullpath):
        """Get local path from fullpath.
        """
        translated = self.re_detailedpath.match(fullpath)
        if not translated:
            raise RuntimeError("translate_fullpath: Could not parse the given url: %s" % fullpath)
        root, folder, path = self.CACHE_DIR, translated.groupdict()["host"], translated.groupdict()["urlpath"][1:]
        localpath = '/'.join([root, folder, path])
        return localpath
    
    def get_cached_source(self, url):
        """Get the cached source for the given url.
        """
        localpath = self.translate_fullpath(url)
        log.debug("get_source: this is my localpath: %s" % localpath)        
        if os.path.isfile(localpath):
            log.debug("get_source: trying to get %s from cache" % localpath)        
            return open(localpath).read()
        raise NotInCacheException
        
    def put_source(self, url, source):
        """Put the source obtained from the given url to cache.
        """
        localpath = self.translate_fullpath(url)        
        dirname = os.path.dirname(localpath)
        log.debug("put_source: trying to create %s" % dirname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        log.debug("put_source: trying to write %s" % localpath)
        open(localpath, "w").write(source)
        log.debug("put_source: wrote %s" % localpath)        
        
        
        
