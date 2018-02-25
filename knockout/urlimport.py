"""
urlimport.py - Enables remote module importing by adding URLs to sys.path.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import sys, re, logging
import imp

from core import Loader, Importer, SilentlyIgnoreException
from urlparse import urljoin
from urllib2 import urlopen

log = logging.getLogger("urlimport")
logging.addLevelName(5, "SOURCE")
SOURCE = 5

class UrlImporter(Importer):
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
                raise SilentlyIgnoreException("Not allowed to import '%s'." % fullname)
            
        fullpath = self.fullpath(fullname, ispkg)
        log.debug("Trying to fetch %s" % fullpath)
        return urlopen(fullpath).read().replace("\r\n", "\n"), fullpath

    def get_loader(self, source, fullpath, ispkg):
        """ Get the loader instance to load the new module.
        """
        return Loader(source, fullpath, ispkg, importer=self)


# register The Hook
def register():
    if UrlImporter.register() != False:
        log.info("Url importing enabled. Add urls to sys.path.")
        log.info("A valid url looks like this: http://example.com/path/to/repository/#packagename")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
