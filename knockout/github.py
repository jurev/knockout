""" Enables remote module importing via github.

To use, add packages to sys.path in the form of:
 - github:user/path#package

"""

import logging
log = logging.getLogger("github")

import sys, os, re, imp

from urlimport import UrlImporter, SOURCE


class GithubImporter(UrlImporter):
    re_fullpath = re.compile(''.join([
        r'^',
        r'(?P<path>github:[^#]+)',
        r'#(?P<package>.+)',
        r'$'
    ]))
    
    def __init__(self, path):
        self._path = path
        m = self.re_fullpath.match(path)
        if m:
            self.path = m.groupdict()["path"]
            self.package = m.groupdict()["package"]
            log.debug("GithubImporter: accepting '%s'." % path)
        else:
            log.debug("GithubImporter: rejecting path item: '%s'" % path)
            raise ImportError
                           
    def fullpath(self, fullname, ispkg):
        repo_name = "/".join(self.path.strip("github:").split("/")[:2])
        path = "/".join(self.path.strip("github:").split("/")[2:])
        if ispkg:
            fullpath = self.join(
                    "https://raw.githubusercontent.com",
                    repo_name,
                    "master",
                    path,
                    fullname.split(".")[-1],
                    "__init__.py"
            )
        else:
            fullpath = self.join(
                    "https://raw.githubusercontent.com",
                    repo_name,
                    "master",
                    path,
                    fullname.split(".")[-1] + ".py",
            )
        return fullpath

    def join(self, *parts):
        return ("/".join(parts))



# register The Hook
def register():
    if GithubImporter.register() != False:
        log.info("Github importing enabled. Add targets to sys.path.")
        log.info("A valid target looks like this: github:path#package")
        log.info("This stuff is experimental, use at your own risk. Enjoy.")


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'github:waylan/Python-Markdown#markdown')
    
    register()
    
    import markdown

