# Python
import os
import sys

# wxPython
import wx
import wx.lib.newevent

# PyWin32
try:
    import win32api
except ImportError:
    win32api = None

# Update path, icon and version based on whether running as a compiled EXE or
# from the source.
if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
    APP_PATH = os.path.dirname(os.path.abspath(sys.executable))
    ICON_PATH = os.path.abspath(sys.executable)
    VERSION = win32api.GetFileVersionInfo(os.path.abspath(sys.executable),
                                          u'\\\\StringFileInfo\\\\040904B0\\\\ProductVersion') or ''
else:
    APP_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ICON_PATH = os.path.join(APP_PATH, 'graphics', 'logo.ico')
    if not os.path.exists(ICON_PATH):
        ICON_PATH = None
    try:
        version = '?'
        for line in open(os.path.join(APP_PATH, 'setup.py'), 'r').readlines():
            if line.strip().startswith('version='):
                version = line.split('=', 1)[1].replace('\'', '').replace(',', '').strip()
    except IOError:
        pass
    VERSION = '{}.dev'.format(version)

APP_NAME = 'BeatDown'
VENDOR_NAME = 'Nine More Minutes, Inc.'

COLOR_BACKGROUND = wx.Colour(0x10, 0x10, 0x10)
COLOR_FOREGROUND = wx.Colour(0x88, 0x88, 0x88)
COLOR_LINES = wx.Colour(0x30, 0x30, 0x30)

ID_INPUT_METER = wx.NewId()

ID_STRENGTH_GAUGE = wx.NewId()
ID_SPEED_DISPLAY = wx.NewId()

ID_AUDIO_INPUT_SELECT = wx.NewId()
ID_STATUS_TEXT = wx.NewId()


AudioServerStartedEvent, EVT_AUDIO_SERVER_STARTED = wx.lib.newevent.NewCommandEvent()
AudioServerStoppedEvent, EVT_AUDIO_SERVER_STOPPED = wx.lib.newevent.NewCommandEvent()

__all__ = [x for x in locals().keys() if x[0].isupper()]
