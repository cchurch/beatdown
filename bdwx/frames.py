# wxPython
import wx
import wx.adv

# BeatDown
from .constants import *  # noqa
from .dialogs import *  # noqa
from .panels import *  # noqa

# PyWin32
try:
    import win32api
    import win32con
    import win32gui
except ImportError:
    win32api, win32con, win32gui = None, None, None

__all__ = ['Frame']


class MenuBar(wx.MenuBar):

    def __init__(self, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q')
        self.Append(file_menu, '&File')
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, '&About')
        self.Append(help_menu, '&Help')


class Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Frame, self).__init__(*args, **kwargs)
        if wx.GetApp().GetIconPath():
            icon = wx.Icon(wx.GetApp().GetIconPath(), wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        self.SetMenuBar(MenuBar())
        sizer = wx.BoxSizer(wx.VERTICAL)
        main_panel = MainPanel(self, wx.ID_ANY)
        sizer.Add(main_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.SetMinSize(self.GetBestSize())
        width = max(wx.GetApp().GetWidth(), self.GetMinWidth())
        height = max(wx.GetApp().GetHeight(), self.GetMinHeight())
        left = wx.GetApp().GetLeft()
        top = wx.GetApp().GetTop()
        screen_x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        screen_y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        if left <= -width or left >= screen_x:
            left = max((screen_x - width) / 2, 0)
        elif left <= -(width / 2):
            left = 0
        elif left >= (screen_x - width / 2):
            left = max(screen_x - width, 0)
        if top <= -height or top >= screen_y:
            top = max((screen_y - height) / 2, 0)
        elif top <= -(height / 2):
            top = 0
        elif top >= (screen_y - height / 2):
            top = max(screen_y - height, 0)
        self.SetPosition((left, top))
        self.SetSize((width, height))
        if wx.GetApp().GetMaximized():
            self.Maximize()
        self.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Bind(wx.EVT_SIZE, self.OnSize, self)
        self.Bind(wx.EVT_MOVE, self.OnMove, self)
        if win32gui:
            self.oldWndProc = win32gui.SetWindowLong(self.GetHandle(),
                                                     win32con.GWL_WNDPROC,
                                                     self.WndProc)

    def OnMenuExit(self, event):
        self.Close(True)

    def OnHelpAbout(self, event):
        info = wx.adv.AboutDialogInfo()
        if wx.GetApp().GetIconPath():
            icon = wx.Icon(wx.GetApp().GetIconPath(), wx.BITMAP_TYPE_ICO)
            info.SetIcon(icon)
        info.SetName('BeatDown')
        info.SetVersion(wx.GetApp().GetVersion())
        info.SetDescription('Beat detection prototype.')
        info.SetCopyright('(c) 2017 Nine More Minutes, Inc.')
        info.SetWebSite('http://www.ninemoreminutes.com')
        wx.adv.AboutBox(info)

    def OnClose(self, event):
        self.Destroy()

    def OnSize(self, event):
        wx.GetApp().SetMaximized(self.IsMaximized())
        if not self.IsMaximized() and not self.IsIconized():
            wx.GetApp().SetWidth(self.GetSize().Get()[0])
            wx.GetApp().SetHeight(self.GetSize().Get()[1])
        event.Skip()

    def OnMove(self, event):
        wx.GetApp().SetMaximized(self.IsMaximized())
        if not self.IsMaximized() and not self.IsIconized():
            wx.GetApp().SetLeft(self.GetPosition().Get()[0])
            wx.GetApp().SetTop(self.GetPosition().Get()[1])
        event.Skip()

    def WndProc(self, hWnd, msg, wParam, lParam):
        if msg == win32con.WM_USER:
            if wParam == 0 and lParam == 1:
                self.Show()
                self.Raise()
        elif msg == win32con.WM_DESTROY:
            win32api.SetWindowLong(self.GetHandle(), win32con.GWL_WNDPROC,
                                   self.oldWndProc)
        return win32gui.CallWindowProc(self.oldWndProc, hWnd, msg, wParam, lParam)
