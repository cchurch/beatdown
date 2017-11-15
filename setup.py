"""Setuptools script for building BeatDown app and installer."""

# Import setuptools before distutils so setuptools can monkey-patch distutils.
import setuptools
from setuptools import setup

# Python
import ctypes
import glob
import os
import sys

# Verify that setup is running on the Windows platform.
if sys.platform == 'win32':

    # Try to import all the 3rd party libraries required:
    import py2exe
    import wx
    import win32api

    # Import addon command for building NSIS installer.
    from py2exe_nsis import py2exe_nsis

    manifest = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <assembly xmlns="urn:schemas-microsoft-com:asm.v1"
    manifestVersion="1.0">
    <assemblyIdentity
        version="0.64.1.0"
        processorArchitecture="x86"
        name="Controls"
        type="win32"
    />
    <description>%s</description>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity
                type="win32"
                name="Microsoft.Windows.Common-Controls"
                version="6.0.0.0"
                processorArchitecture="X86"
                publicKeyToken="6595b64144ccf1df"
                language="*"
            />
        </dependentAssembly>
    </dependency>
    </assembly>
    """

    # Explicitly exclude Windows DLLs that py2exe includes by default.
    dll_excludes = ['MSVCP90.dll', 'w9xpopen.exe', 'kernelbase.dll', 'powrprof.dll', 'mswsock.dll']
    for f in glob.glob(os.path.join(win32api.GetSystemDirectory(), 'API-MS-Win*.dll')):
        dll_excludes.append(f)

    # Include the CRT DLLs and manifest.
    crt_path = os.path.join(os.path.dirname(__file__), 'dlls', 'Microsoft.VC90.CRT')
    crt_files = glob.glob(os.path.join(crt_path, 'msvc*.dll'))
    crt_files.extend(glob.glob(os.path.join(crt_path, 'Microsoft.VC90.CRT.manifest')))

    # Include the MFC DLLs and manifest.
    mfc_path = os.path.join(os.path.dirname(__file__), 'dlls', 'Microsoft.VC90.MFC')
    mfc_files = glob.glob(os.path.join(mfc_path, 'mfc*.dll'))
    mfc_files.extend(glob.glob(os.path.join(mfc_path, 'Microsoft.VC90.MFC.manifest')))

    # From: http://www.py2exe.org/index.cgi/win32com.shell
    # ModuleFinder can't handle runtime changes to __path__, but win32com uses them
    try:
        try:
            import py2exe.mf as modulefinder
        except ImportError:
            import modulefinder
        import win32com
        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath('win32com', p)
        for extra in ['win32com.shell']: #,"win32com.mapi"
            __import__(extra)
            m = sys.modules[extra]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(extra, p)
    except ImportError:
        pass

    platform_options = dict(
        setup_requires=[
            #'py2exe==0.6.9',
        ],
        windows=[
            dict(
                script='beatdown.py',
                dest_base='beatdown',
                icon_resources=[
                    (0, '../graphics/logo.ico'),
                ],
                other_resources=[
                    #(24, 1, manifest % 'beatdown'),
                    ('beatdown', 1, file('./graphics/logo.png', 'rb').read()),
                ]
            ),
        ],
        options={
            'py2exe': {
                'dll_excludes': dll_excludes,
                'excludes': ['Tkconstants', 'Tkinter', 'tcl'],
                'packages': ['bdwx'],
                'bundle_files': 3,
            },
            'py2exe_nsis': {
                'dist_dir': 'build_output',
            },
            'sdist': {
                'dist_dir': 'build_output',
                'formats': 'zip',
            },
            'egg_info': {
                'tag_svn_revision': 1,
                'tag_build': '.dev',
            },
            'aliases': {
                'dev_build': 'egg_info sdist py2exe_nsis',
                'release_build': ' egg_info -b "" sdist py2exe_nsis',
            },
        },
        data_files=[
            #('Microsoft.VC90.CRT', crt_files),
            #('Microsoft.VC90.MFC', mfc_files),
        ],
        zipfile='beatdown.pyz',
        cmdclass={'py2exe_nsis': py2exe_nsis},
    )
else:
    platform_options = {}


setup(
    name='BeatDown',
    version='0.1.0',
    description='Tool for audio analysis to generate MIDI messages.',
    long_description='',
    author='Nine More Minutes, Inc.',
    author_email='chris@ninemoreminutes.com',
    license='Apache 2.0',
    url='http://www.ninemoreminutes.com/',
    **platform_options
)
