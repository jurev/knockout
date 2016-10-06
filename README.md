## Knockout

Knockout aims to extend the basic importing mechanisms in Python by allowing more exotic stuff to be added to sys.path.

### Importers

Currently, the available importers are:

- *urlimport.py*: Import modules from anywhere on the web by adding URLs to sys.path.
- *github.py*: Import modules from Github repositories.

### Importing modules from the web	
	
	>>> from knockout import urlimport
	>>> urlimport.register()
	Url importing enabled. Add urls to sys.path.
	A valid url looks like this: http://example.com/path/to/repository/#packagename
	This stuff is experimental, use at your own risk. Enjoy.
	
	>>> import sys
	>>> sys.path.insert(0, 'http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.8/#BeautifulSoup')
	>>> import BeautifulSoup
	...
	
	>>> BeautifulSoup
	<module 'BeautifulSoup' from 'http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.8/BeautifulSoup.py'>
	
### Importing modules from Github

    >>> from knockout import github
    >>> github.register()
    Github importing enabled. Add targets to sys.path.
    A valid target looks like this: github:path#package
    This stuff is experimental, use at your own risk. Enjoy.
    >>> import sys
    >>> sys.path.insert(0, 'github:waylan/Python-Markdown#markdown')
    >>> import markdown
    ...

    >>> markdown.markdown("foo")
    u'<p>foo</p>'
	
	
