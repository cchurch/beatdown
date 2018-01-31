# wxPython
import wx
import wx.lib.agw.floatspin

# BeatDown
from .constants import *  # noqa
from .utils import *  # noqa


class MidiNoteTextCtrlProxy(object):

    def __init__(self, wrapped):
        self.__dict__['_wrapped'] = wrapped

    def _unwrap(self):
        return self._wrapped

    def GetValue(self):
        res = self._wrapped.GetValue()
        try:
            res = str(float(midi_note_to_int(res)))
        except ValueError:
            pass
        return res

    def SetValue(self, value):
        try:
            value = int_to_midi_note(value)
        except ValueError:
            pass
        self._wrapped.SetValue(value)

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        delattr(self._wrapped, name)


class MidiNoteSpinCtrl(wx.lib.agw.floatspin.FloatSpin):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(95, -1), style=0, value=0.0, min_val=0.0, max_val=127.0,
                 increment=1.0, digits=0, agwStyle=wx.lib.agw.floatspin.FS_LEFT,
                 name='MidiNoteSpinCtrl'):
        super(MidiNoteSpinCtrl, self).__init__(parent, id, pos, size, style,
                                               value, min_val, max_val,
                                               increment, digits, agwStyle, name)

        self._validkeycode_original = [kc for kc in self._validkeycode]
        self._validkeycode_notes = [kc for kc in self._validkeycode if kc not in (43, 44, 46)]
        for keycode in [35, 65, 66, 67, 68, 69, 70, 71, 72, 73, 97, 98, 99, 100, 101, 102, 103, 104, 105]:
            if keycode not in self._validkeycode_notes:
                self._validkeycode_notes.append(keycode)

    def EnableNotes(self, enable=True):
        if enable and not hasattr(self._textctrl, '_wrapped'):
            self._textctrl = MidiNoteTextCtrlProxy(self._textctrl)
            self._textctrl.SetValue(str(self._textctrl.GetValue()))
            self._validkeycode = self._validkeycode_notes
        elif not enable and hasattr(self._textctrl, '_unwrap'):
            self._textctrl = self._textctrl._unwrap()
            value = self.GetValue()
            self._value = None
            self.SetValue(value)
            self._validkeycode = self._validkeycode_original

    def DisableNotes(self):
        return self.EnableNotes(False)


class BeatDisplay(wx.Window):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(-1, 30), style=0):
        super(BeatDisplay, self).__init__(parent, id, pos, size, style)

        self._size = size
        self._value = None
        self._inactive_colour = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def GetValue(self):
        return self._value

    def SetValue(self, value):
        if value is None:
            self._value = value
        else:
            try:
                self._value = min(95, max(0, int(value)))
            except (TypeError, ValueError):
                pass

    def NextClock(self):
        value = self.GetValue()
        self.SetValue(0 if value is None else (value + 1) % 96)

    def GetInactiveColour(self):
        if self._inactive_colour is None:
            self.SetInactiveColour(None)
        return self._inactive_colour

    def SetInactiveColour(self, colour):
        if colour is None:
            colour = wx.Colour(self.GetForegroundColour())
            colour.MakeDisabled(32)
            self._inactive_colour = colour
        else:
            self._inactive_colour = wx.Colour(colour)

    GetInactiveColor = GetInactiveColour
    SetInactiveColor = SetInactiveColour

    def DoGetBestSize(self):
        return wx.Size(self._size[0], self._size[1])

    def OnEraseBackground(self, event):
        pass

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        rect = self.GetClientRect()

        fg_color = self.GetForegroundColour()
        bg_color = self.GetBackgroundColour()
        in_color = self.GetInactiveColour()

        in_color1 = wx.Colour(fg_color)
        in_color1.MakeDisabled(128)
        in_color2 = wx.Colour(fg_color)
        in_color2.MakeDisabled(64)

        dc.SetBackground(wx.Brush(bg_color))
        dc.Clear()
        dc.SetBrush(wx.Brush(bg_color))
        dc.SetPen(wx.Pen(bg_color))
        dc.DrawRectangle(rect)

        left = 4.0
        for clock in range(96):
            offset = 0.0
            if clock % 24 == 0:
                radius = 4.0
            elif clock % 12 == 0:
                radius = 2.0
            elif clock % 6 == 0:
                radius = 1.0
                if clock % 24 == 6:
                    offset = 1.0
                elif clock % 24 == 18:
                    offset = -1.0
            elif clock % 3 == 0:
                radius = 0.5
                if clock % 24 == 3:
                    offset = 2.0
                elif clock % 24 == 21:
                    offset = -2.0
            else:
                radius = 0.0

            circle_radius = rect.width * radius / 100
            if circle_radius >= 1.2:

                if self._value is not None:
                    active = [x % 96 for x in range(self._value - 2, self._value + 1)]
                    inactive1 = [x % 96 for x in range(self._value - 11, self._value - 2)]
                    inactive2 = [x % 96 for x in range(self._value - 23, self._value - 11)]
                    if clock in active:
                        color = fg_color
                    elif clock in inactive1:
                        color = in_color1
                    elif clock in inactive2:
                        color = in_color2
                    else:
                        color = in_color
                else:
                    color = in_color
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))

                circle_left = rect.width * (left + offset) / 100
                circle_top = rect.height * 0.5
                dc.DrawCircle(circle_left, circle_top, circle_radius)

            left += 1.0
