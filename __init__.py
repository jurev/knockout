"""
Knockout is a set of modules that extend Python's import mechanisms in various ways.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import sys, os, re
import imp

import logging
SOURCE = 5
logging.addLevelName(SOURCE, "SOURCE")
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class Loader:
    """ A basic module loader.
    """

    def __init__(self, source, fullpath, ispkg, importer=None):
        self.source = source
        self.fullpath = fullpath
        self.ispkg = ispkg
        self.importer = importer

    def load_module(self, fullname):
        """ Add the new module to sys.modules,
            execute its source and return it.
        """

        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        mod.__file__ = self.fullpath
        mod.__loader__ = self
        if self.ispkg and self.importer:
            mod.__path__ = [self.importer.join(self.importer.path, fullname.split(".")[-1])]

        #for line in self.source.split('\n'):
        #    log.log(SOURCE, "%s %s" %('|>|', line))

        log.debug("load_module: executing %s's source..." % fullname)

        try:
            exec self.source in mod.__dict__
        except:
            if fullname in sys.modules:
                del sys.modules[fullname]
            raise
        
        mod = sys.modules[fullname]
        return mod


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
            self.__dict__.update(m.groupdict())
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
        loader = None
        for ispkg in [False, True]:
            try:
                source, fullpath = self.get_source(fullname, ispkg=ispkg)
                loader = self.get_loader(source, fullpath, ispkg)
            except Exception, e:
                self.debug("find_module: %s: failed to get '%s'. (%s)" % ({True: 'PKG', False: 'MOD'}.get(ispkg), fullname, e))
            else:
                self.debug("find_module: %s: got '%s'. mpath=%s" % ({True: 'PKG', False: 'MOD'}.get(ispkg), fullname, mpath))            
                break
        return loader

    def debug(self, str):
        log.debug("%s: %s" % (self.__class__.__name__, str))


    # -- stuff to override

    def fullpath(self, fullname, ispkg):
        if ispkg:
            fullpath = self.join(self.path, fullname.split(".")[-1]) + "/__init__.py"
        else:
            fullpath = self.join(self.path, fullname.split(".")[-1]) + ".py"
        return fullpath

    def join(self, *parts):
        return os.path.join(*parts)

    def get_source(self, fullname, ispkg):
        """ Get the source for the new module to be loaded.
        """
        fullpath = self.fullpath(fullname, ispkg)
        return open(fullpath).read().replace("\r\n", "\n"), fullpath

    def get_loader(self, source, fullpath, ispkg):
        """ Get the loader instance to load the new module.
        """
        return Loader(source, fullpath, ispkg, importer=self)


# register The Hook
def register():
    if Importer.register() != False:
        log.info("Custom importer enabled.")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
