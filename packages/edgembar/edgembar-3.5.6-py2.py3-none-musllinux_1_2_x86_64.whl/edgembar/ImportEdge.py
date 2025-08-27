#!/usr/bin/env python3
from . Edge import Edge

def ImportEdge( pyfilename: str ) -> Edge:
    import importlib.machinery
    import importlib.util
    import importlib
    import os
    import errno
    import sys
    sys.dont_write_bytecode = True

    if not os.path.isfile(pyfilename):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), pyfilename)
    
    modname = pyfilename.replace(".","d").replace("-","h")
    modname = modname.replace("_","u")
    modname = modname.replace("/","s").replace("\\","b")
    modname = modname.replace("~","t").replace("#","o")
    modname = modname.replace("@","a").replace("%","p")
    #spec = importlib.util.spec_from_file_location(modname, pyfilename)
    #usermod = importlib.util.module_from_spec(spec)
    #spec.loader.exec_module(usermod)
    #print("Reading",pyfilename,"as",modname)
    
    importlib.invalidate_caches()
    loader = importlib.machinery.SourceFileLoader(modname,pyfilename)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    usermod = importlib.util.module_from_spec(spec)
    loader.exec_module(usermod)
    #print(usermod)
    #exit(0)
    return usermod.edge
