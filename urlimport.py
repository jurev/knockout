"""
urlimport.py - Enables remote module importing by adding URLs to sys.path.

See PEP 302(http://www.python.org/dev/peps/pep-0302/) for more info.
"""

import sys, re
import knockout
from urlparse import urljoin
from urllib2 import urlopen

log = knockout.log

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
        name = fullname.split(".")[-1]
        if self.package != '__all__' and name != self.package:
            raise Exception("Not allowed to import '%s'." % fullname)
            
        fullpath = self.fullpath(fullname, ispkg)
        return urlopen(fullpath).read().replace("\r\n", "\n"), fullpath

    def get_loader(self, source, fullpath, ispkg):
        """ Get the loader instance to load the new module.
        """
        return knockout.Loader(source, fullpath, ispkg, importer=self)


# register The Hook
def register():
    if UrlImporter.register() != False:
        log.info("Url importing enabled. Add urls to sys.path.")
        log.info("A valid url looks like this: http://example.com/path/to/repository/#packagename")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")
    
def clear_cache():        
    sys.path_importer_cache.clear()


#register()
