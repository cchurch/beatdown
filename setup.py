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

    # MSP430 dll files.
    dll_path = os.path.join(os.path.dirname(__file__))
    dll_files = glob.glob(os.path.join(dll_path, '*.dll'))

    # MSP430 firmware files.
    fw_path = os.path.join(os.path.dirname(__file__), 'firmware')
    fw_files = glob.glob(os.path.join(fw_path, '*.hex*'))

    # Sound WAV files.
    wav_path = os.path.join(os.path.dirname(__file__))
    wav_files = glob.glob(os.path.join(wav_path, '*.wav'))

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
                script='progone.py',
                dest_base='progone',
                icon_resources=[
                    (0, '../graphics/progone.ico'),
                ],
                other_resources=[
                    #(24, 1, manifest % 'progone'),
                    ('progone', 1, file('../graphics/progone.png', 'rb').read()),
                    ('progone', 2, file('../graphics/twelve24.jpg', 'rb').read()),
                    ('progone', 3, file('../graphics/spinner.png', 'rb').read()),
                    ('progone', 4, file('../graphics/success.png', 'rb').read()),
                    ('progone', 5, file('../graphics/error.png', 'rb').read()),
                    ('progone', 6, file('../graphics/digit-blank.png', 'rb').read()),
                    ('progone', 7, file('../graphics/digit-normal-0.png', 'rb').read()),
                    ('progone', 8, file('../graphics/digit-normal-1.png', 'rb').read()),
                    ('progone', 9, file('../graphics/digit-normal-2.png', 'rb').read()),
                    ('progone', 10, file('../graphics/digit-normal-3.png', 'rb').read()),
                    ('progone', 11, file('../graphics/digit-normal-4.png', 'rb').read()),
                    ('progone', 12, file('../graphics/digit-normal-5.png', 'rb').read()),
                    ('progone', 13, file('../graphics/digit-normal-6.png', 'rb').read()),
                    ('progone', 14, file('../graphics/digit-normal-7.png', 'rb').read()),
                    ('progone', 15, file('../graphics/digit-normal-8.png', 'rb').read()),
                    ('progone', 16, file('../graphics/digit-normal-9.png', 'rb').read()),
                    ('progone', 17, file('../graphics/digit-normal-b.png', 'rb').read()),
                    ('progone', 18, file('../graphics/digit-normal-A.png', 'rb').read()),
                    ('progone', 19, file('../graphics/digit-normal-t.png', 'rb').read()),
                    ('progone', 20, file('../graphics/digit-blackout-0.png', 'rb').read()),
                    ('progone', 21, file('../graphics/digit-blackout-1.png', 'rb').read()),
                    ('progone', 22, file('../graphics/digit-blackout-2.png', 'rb').read()),
                    ('progone', 23, file('../graphics/digit-blackout-3.png', 'rb').read()),
                    ('progone', 24, file('../graphics/digit-blackout-4.png', 'rb').read()),
                    ('progone', 25, file('../graphics/digit-blackout-5.png', 'rb').read()),
                    ('progone', 26, file('../graphics/digit-blackout-6.png', 'rb').read()),
                    ('progone', 27, file('../graphics/digit-blackout-7.png', 'rb').read()),
                    ('progone', 28, file('../graphics/digit-blackout-8.png', 'rb').read()),
                    ('progone', 29, file('../graphics/digit-blackout-9.png', 'rb').read()),
                    ('progone', 30, file('../graphics/digit-blackout-b.png', 'rb').read()),
                    ('progone', 31, file('../graphics/digit-blackout-A.png', 'rb').read()),
                    ('progone', 32, file('../graphics/digit-blackout-t.png', 'rb').read()),
                    ('progone', 33, file('../graphics/digit-test-0.png', 'rb').read()),
                    ('progone', 34, file('../graphics/digit-test-1.png', 'rb').read()),
                    ('progone', 35, file('../graphics/digit-test-2.png', 'rb').read()),
                    ('progone', 36, file('../graphics/digit-test-3.png', 'rb').read()),
                    ('progone', 37, file('../graphics/digit-test-4.png', 'rb').read()),
                ]
            ),
        ],
        options={
            'py2exe': {
                'dll_excludes': dll_excludes,
                'excludes': ['Tkconstants', 'Tkinter', 'tcl'],
                'packages': ['progoneui'],
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
            ('', dll_files),
            ('', wav_files),
            ('firmware', fw_files),
        ],
        zipfile='progone.pyz',
        cmdclass={'py2exe_nsis': py2exe_nsis},
    )
else:
    platform_options = {}


setup(
    name='ProgrammerONE',
    version='0.1.0',
    description='Flash programmer for ClockONE',
    long_description='User interface for factory programming and testing of ClockONE display.',
    author='Octa LLC',
    author_email='cchurch@octallc.com',
    license='Proprietary',
    url='http://www.octallc.com/',
    **platform_options
)
