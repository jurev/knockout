from SimpleHTTPServer import test, SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import os, sys

def serve(path):
    os.chdir(path)
    test()

if __name__ == "__main__":
    serve("test/remote_files")