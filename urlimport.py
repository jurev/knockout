"""
urlimport.py - Enables remote module importing by adding URLs to sys.path.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import logging
SOURCE = 5
logging.addLevelName(SOURCE, "SOURCE")
logging.basicConfig(level=SOURCE)
log = logging.getLogger("urlimport")

import sys, re
import imp


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
    
    As a master importer, this class has access to all available importers.
    """
    __metaclass__ = ImporterMeta

    re_fullpath = re.compile('foo://bar/baz')

    def __init__(self, path):
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

    @property
    def fullpath(self):
        raise NotImplementedError("This should return a string representing the current path.")

    def find_module(self, fullname, mpath=None):
        raise NotImplementedError("This should return self if module found, else None.")

    def get_source(self, fullpath):
        raise NotImplementedError("This should return the source as a string.")

    def load_module(self, fullname):
        raise NotImplementedError("This should put the module in sys.modules and return it.")

        
class UrlImporter(Importer):
    re_fullpath = re.compile(''.join([
        r'^',
        r'(?P<location>(http|ftp)://[^#]+)',
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

        exec self.source in mod.__dict__

        mod = sys.modules[fullname]
        return mod


# register The Hook
def register():
    if UrlImporter.register() != False:
        log.info("Url importing enabled. Add urls to sys.path.")
        log.info("A valid url looks like this: http://example.com/path/to/repository/#packagename")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
