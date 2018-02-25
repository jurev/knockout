## Knockout

Knockout aims to extend the basic importing mechanisms in Python3 by allowing more exotic stuff to be added to sys.path.

### TODO

- add tests
- PyPy support with sandbox mode
- Hy support

### Importers

Currently, the available importer is:

- *urlimport.py*: Import modules from anywhere on the web by adding URLs to sys.path.

### Importing modules from the web	
	
	>>> from knockout import urlimport
	>>> urlimport.register()
	Url importing enabled. Add urls to sys.path.
	A valid url looks like this: http://example.com/path/to/repository/#packagename
	This stuff is experimental, use at your own risk. Enjoy.
	
	>>> import sys
	>>> sys.path.insert(0, 'http://localhost:8000/#import_me')
	>>> import import_me
	...

	
