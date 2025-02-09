import os

def pre_init():
    library_paths = ['/usr/local/lib', '/opt/homebrew/lib']
    os.environ['DYLD_LIBRARY_PATH'] = ':'.join(library_paths)