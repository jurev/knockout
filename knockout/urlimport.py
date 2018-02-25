"""
urlimport.py - Enables remote module importing by adding URLs to sys.path.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import sys, re, logging
import imp

import knockout
from urlparse import urljoin
from urllib2 import urlopen

log = logging.getLogger("urlimport")
logging.addLevelName(5, "SOURCE")
SOURCE = 5

class URLLoader:
    """ A basic URL module loader.
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
            mod.__path__ = [self.importer.join(self.importer.path, fullname.split(".")[-1] + "/#__all__")]

        for line in self.source.split('\n'):
            log.log(SOURCE, "%s %s" %('|>|', line))

        log.debug("load_module: executing %s's source..." % fullname)

        try:
            exec self.source in mod.__dict__
        except:
            if fullname in sys.modules:
                del sys.modules[fullname]
            raise
        
        mod = sys.modules[fullname]
        return mod


class UrlImporter(knockout.Importer):
    re_fullpath = re.compile(''.join([
        r'^',
        r'(?P<path>(http|https|ftp)://[^#]+)',
        r'#(?P<package>.+)',
        r'$'
    ]))

    
    def join(self, *parts):
        return urljoin(*parts)

    def get_source(self, fullname, ispkg):
        """Download the source for the new module to be loaded.
        """
        # are we allowed to download this module?
        if "." not in fullname:
            if self.package != '__all__' and fullname != self.package:
                raise Exception("Not allowed to import '%s'." % fullname)
            
        fullpath = self.fullpath(fullname, ispkg)
        log.debug("Trying to fetch %s" % fullpath)
        return urlopen(fullpath).read().replace("\r\n", "\n"), fullpath

    def get_loader(self, source, fullpath, ispkg):
        """ Get the loader instance to load the new module.
        """
        return URLLoader(source, fullpath, ispkg, importer=self)


# register The Hook
def register():
    if UrlImporter.register() != False:
        log.info("Url importing enabled. Add urls to sys.path.")
        log.info("A valid url looks like this: http://example.com/path/to/repository/#packagename")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
