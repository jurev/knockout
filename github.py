""" Enables remote module importing via github.

To use, add packages to sys.path in the form of:
 - github:#user
 - github:user#package
 - github:user/package#subpackage

"""

import logging
log = logging.getLogger("github")

import sys, os, re, imp

from urlimport import UrlImporter, SOURCE


class GithubImporter(UrlImporter):
    re_fullpath = re.compile(''.join([
        r'^github:',
        r'(?P<path>[^#]+)',
        r'#(?P<package>.+)',
        r'$'
    ]))
    
    def __init__(self, path):
        self._path = path
        m = self.re_fullpath.match(path)
        if m:
            self.path = m.groupdict()["path"]
            self.package = m.groupdict()["package"]
            self.realpath = self.expand_path()
            log.debug("GithubImporter: accepting '%s'." % path)
        else:
            #log.debug("UrlImporter: rejecting path item: '%s'" % path)
            raise ImportError
            
    @property
    def user(self):
        u = self.path.split("/")
        if not u:
            return None
        return u[0]

    @property
    def repository(self):
        r = self.path.split("/")
        if not r[1:]:
            return None
        return r[1]

    def expand_path(self, name=''):
        """
        >>> i = GithubImporter("github:jurev#knockout")
        >>> i.expand_path()
        'https://github.com/jurev/'
        >>> i.expand_path("knockout")
        'https://github.com/jurev/knockout/'
        >>> i = GithubImporter("github:mitsuhiko/jinja2/jinja2#utils")
        >>> i.expand_path()
        'https://github.com/mitsuhiko/jinja2/raw/master/jinja2/'
        """
        parts = self.path.split("/") + name.split("/") + [None]*5
        expanded = "https://github.com/"
        if parts[0]:
            expanded += parts[0] + "/" # user
        if parts[1]:
            expanded += parts[1] + "/" # repository
        if parts[2]:
            expanded += "raw/master/"
            expanded += '/'.join(filter(None, parts[2:])) # module
        return expanded
    
    def extend_path(self, name):
        """
        >>> i = GithubImporter("github:jurev#knockout")
        >>> i.extend_path("knockout")
        'github:jurev/knockout/#__all__'
        >>> i.extend_path("knockout/test/")
        'github:jurev/knockout/test/#__all__'
        """
        return 'github:' + os.path.join(self.path, name, "#__all__")
    
    def get_candidates(self, fullname):
        name = fullname.split('.')[-1]
         
        # check if name is allowed to be imported
        if self.package != "__all__" and name != self.package:
            #log.debug("find_module: not allowed to import '%s%s'." % (self.fullpath, name))
            raise StopIteration
        
        if not self.user:
            yield "<github>", self.extend_path(name)
        else:
            for url, path in [
             (self.expand_path(name + '.py'),          None),
             (self.expand_path(name + '/__init__.py'), self.extend_path(name))]:
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
                if path:
                    self.path = path
                self.__file__ = url
                return self

        return None

    def get_source(self, url):
        """Download the source from given url.
        """
        if url == '<github>':
            return "\n"
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
    if GithubImporter.register() != False:
        log.info("Github importing enabled. Add targets to sys.path.")
        log.info("A valid target looks like this: github:user#package")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")



"""

Head commit of the master branch:  
https://github.com/jurev/knockout/raw/master/urlimport.py

A bb6..845 commit in the magic branch:
https://github.com/jurev/knockout/raw/magic/bb6..845/urlimport.py

"""


if __name__ == '__main__':
    import sys
    #sys.path.insert(-1, 'github:jurev#sweetsoup')
    #sys.path.insert(-1, 'github:#jurev')
    sys.path.insert(-1, 'github:defunkt/pystache#pystache')
    
    register()
    
    import pystache
    
    #import sweetsoup
    #print sweetsoup
    
