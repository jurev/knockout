from gaeimport import FileCacheImporter as MyImporter

def register(cache_dir="knocked", symlinks_dir=None):
    MyImporter.CACHE_DIR = cache_dir
    MyImporter.SYMLINKS_DIR = symlinks_dir
    MyImporter.register()
