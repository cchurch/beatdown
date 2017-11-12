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
