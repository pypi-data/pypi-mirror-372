from setuptools import setup, Extension
from shutil import which

import os
import pathlib

if ('SOURCE_ONLY_BUILD' in os.environ):
    sourceOnlyBuild = True
else:
    sourceOnlyBuild = False

unableToLocate = '\
Error: Unable to locate the Actian Zen installation.  To use this package\n\
    an Actian Zen Client or Server must be installed locally.  To download\n\
    Actian Zen visit https://esd.actian.com/product.  If Actian Zen is\n\
    already installed locally ensure that the PATH environment variable\n\
    is set appropriately.  On some systems the LD_LIBRARY_PATH environment\n\
    variable must be set appropriately as well.\
'

platform = None

if (sourceOnlyBuild == True):
    zenLibraryDir = '.'
else:
    platform = None

    # If running on Windows.
    if os.name == 'nt':
        whichPath = which('w64clilcadm')

        if (whichPath != None):
            platform = 'win64'
        else:
            whichPath = which('clilcadm')

            if (whichPath != None):
                platform = 'win32'
    else:
        whichPath = which('clilcadm64')

        if (whichPath != None):
            platform = 'linux64'
        else:
            whichPath = which('clilcadm')

            if (whichPath != None):
                platform = 'linux32'

    if (platform == 'win64') or (platform == 'win32'):
        zenLibraryDir = os.path.dirname(whichPath) # C:\Program Files\Actian\Zen\bin

        # Symbolic link any necessary DLLs since "runtime_library_dirs" isn't currently supported on Windows.
        # This allows the DLLs to be found when loading the btrievePython extension.
        for item in os.listdir(zenLibraryDir):
            if (pathlib.Path(item).suffix == '.dll'):
                src = os.path.join(zenLibraryDir, item)
                dst = os.path.join('btrievePython', item)

                if (os.path.isfile(dst) == False):
                    os.symlink(src, dst)
    elif (platform == 'linux64'):
        zenLibraryDir = os.path.dirname(whichPath)     # /usr/local/actianzen/bin
        zenLibraryDir = os.path.dirname(zenLibraryDir) # /usr/local/actianzen
        zenLibraryDir += '/lib64'                      # /usr/local/actianzen/lib64
    elif (platform == 'linux32'):
        zenLibraryDir = os.path.dirname(whichPath)     # /usr/local/actianzen/bin
        zenLibraryDir = os.path.dirname(zenLibraryDir) # /usr/local/actianzen
        zenLibraryDir += '/lib'                        # /usr/local/actianzen/lib
    else:
        print(unableToLocate)
        exit(1)

if (platform == 'win64'):
    setup(
        packages=['btrievePython'],
        ext_modules = [
            Extension(
                name = 'btrievePython._btrievePython',
                sources = [ 'btrievePython/btrievePython.cpp' ],
                library_dirs = [ 'btrievePython/win64', zenLibraryDir ],
                # Not currently supported on Windows.  
                #runtime_library_dirs = [ zenLibraryDir ],
                libraries = [ 'btrieveCpp' ]
            )
        ]
    )
elif (platform == 'win32'):
    setup(
        packages=['btrievePython'],
        ext_modules = [
            Extension(
                name = 'btrievePython._btrievePython',
                sources = [ 'btrievePython/btrievePython.cpp' ],
                library_dirs = [ 'btrievePython/win32', zenLibraryDir ],
                # Not currently supported on Windows.  
                #runtime_library_dirs = [ zenLibraryDir ],
                libraries = [ 'btrieveCpp' ]
            )
        ]
    )
else:
    setup(
        packages=['btrievePython'],
        ext_modules = [
            Extension(
                name = 'btrievePython._btrievePython',
                sources = [ 'btrievePython/btrievePython.cpp' ],
                library_dirs = [ 'btrievePython', zenLibraryDir ],
                runtime_library_dirs = [ zenLibraryDir ],
                libraries = [ 'btrieveCpp' ]
            )
        ]
    )
