"""
Knockout is a set of modules that extend Python's import mechanisms in various ways.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import sys, os, re
import imp
import logging
logging.basicConfig()
log = logging.getLogger()

class ImporterMeta(type):
    """ A metaclass for all importers.
    
    """
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'importers'):
            cls.importers = []
        else:
            cls.importers.append(cls)

class Importer:
    """ The base for all other importers.

    Implements the standard Python import mechanism.
    
    As a master importer, this class has access to all available importers.
    """
    __metaclass__ = ImporterMeta

    re_fullpath = re.compile(r'^(?P<path>.+)$')

    # -- private stuff

    def __init__(self, path):
        m = self.re_fullpath.match(path)
        if m:
            self.fullname = None
            self.ispkg = False
            self.path = m.groupdict()["path"]
            self.debug("accepting '%s'." % path)
        else:
            self.debug("rejecting path item: '%s'" % path)
            raise ImportError

    @classmethod
    def register(cls):
        """ Register this class as an active importer.
        """
        if cls in sys.path_hooks:
            log.warning("%s: I am already registered." % cls)
            return False
        sys.path_hooks.append(cls)

    @classmethod
    def unregister(cls):
        """ Unregister this class. It will no longer be able to import modules.
        """
        if not cls in sys.path_hooks:
            log.warning("%s: I am not registered." % cls)
            return False
        sys.path_hooks.delete(cls)

    def find_module(self, fullname, mpath=None):
        self.fullname = fullname
        for loader in self.gen_loaders():
            try:
                loader.get_source()
            except Exception, e:
                self.debug("find_module: failed to get '%s'. (%s)" % (self.fullpath(), e))
            else:
                self.debug("find_module: got '%s'. mpath=%s" % (self.fullpath(), mpath))

                return loader

    def load_module(self, fullname):
        """ Add the new module to sys.modules,
         execute its source and return it.
        """

        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        mod.__file__ = self.fullpath()
        mod.__loader__ = self
        if self.ispkg:
            mod.__path__ = [self.join(self.path, self.name)]

        #for line in self.source.split('\n'):
        #    log.log(SOURCE, "%s %s" %('|>|', line))

        self.debug("load_module: executing %s's source..." % fullname)

        exec self.source in mod.__dict__

        mod = sys.modules[fullname]
        return mod

    
    def debug(self, str):
        log.debug("%s: %s" % (self.__class__.__name__, str))


    # -- stuff to override

    def fullpath(self):
        if self.ispkg:
            fullpath = os.path.join(self.path, self.fullname.split(".")[-1]) + "/__init__.py"
        else:
            fullpath = os.path.join(self.path, self.fullname.split(".")[-1]) + ".py"
        return fullpath

    def join(self, *parts):
        return os.path.join(*parts)

    def gen_loaders(self):
        name = self.fullname.split('.')[-1]
        self.name = name
        
        # <path>/<name>.py
        self.ispkg = False
        yield self
        
        # <path>/<name>/__init__.py
        self.ispkg = True
        yield self

    def get_source(self):
        """ Get the source for the new module to be loaded.
        """
        fullpath = self.fullpath()
        self.source = open(fullpath).read().replace("\r\n", "\n")
        return True
        
class UrlImporter(Importer):
    re_fullpath = re.compile(''.join([
        r'^',
        r'(?P<location>(http|https|ftp)://[^#]+)',
        r'#(?P<package>.+)',
        r'$'
    ]))

    def __init__(self, path):
        m = self.re_fullpath.match(path)
        if m:
            self.location = m.groupdict()["location"]
            self.package = m.groupdict()["package"]
            self.basepath = self.fullpath
            log.debug("UrlImporter: accepting '%s'." % path)
        else:
            #log.debug("UrlImporter: rejecting path item: '%s'" % path)
            raise ImportError

    @property
    def fullpath(self, with_package=False):
        url = "%s" % (self.location)
        if with_package:
            url += "#%s" % self.package
        return url

    def get_candidates(self, fullname):
        name = fullname.split('.')[-1]
         
        # check if name is allowed to be imported
        if self.package != "__all__" and name != self.package:
            #log.debug("find_module: not allowed to import '%s%s'." % (self.fullpath, name))
            raise StopIteration
        
        for url, path in [
         (self.fullpath + name + '.py',          None),
         (self.fullpath + name + '/__init__.py', self.fullpath + name + "/#__all__")]:
            yield url, path
           
    def find_module(self, fullname, mpath=None):
        """try to locate the remote module, do this:
         a) try to get name.py from self.url
         b) try to get __init__.py from self.url/name/
        """
            
        for url, path in self.get_candidates(fullname):
            try:
                self.source = self.get_source(url)
            except Exception, e:
                log.debug("find_module: failed to get '%s'. (%s)" % (url, e))
            else:
                log.debug("find_module: got '%s'. mpath=%s" % (url, mpath))
                self.path = path
                self.__file__ = url
                return self

        return None

    def get_source(self, url):
        """Download the source from given url.
        """
        from urllib2 import urlopen
        return urlopen(url).read().replace("\r\n", "\n")

    def load_module(self, fullname):
        """ Add the new module to sys.modules,
         execute its source and return it.
        """

        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        mod.__file__ = "%s" % self.__file__
        mod.__loader__ = self
        if self.path:
            mod.__path__ = [self.path]

        for line in self.source.split('\n'):
            log.log(SOURCE, "%s %s" %('|>|', line))

        log.debug("load_module: executing %s's source..." % fullname)

        exec self.source.strip() in mod.__dict__

        mod = sys.modules[fullname]
        return mod


# register The Hook
def register():
    if lImporter.register() != False:
        log.info("Custom importer enabled.")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
