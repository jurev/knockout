## Knockout

Knockout aims to extend the basic importing mechanisms in Python by allowing more exotic stuff to be added to sys.path.

### Importers

Currently, the available importers are:

- *urlimport.py*: Import modules from anywhere on the web by adding URLs to sys.path.

### Basic usage	
	
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