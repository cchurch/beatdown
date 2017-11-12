# wxPython
import wx

# BeatDown
from .constants import *  # noqa
from .controls import *  # noqa

__all__ = ['MidiCommandDialog']


class MidiCommandDialog(wx.Dialog):

    COMMAND_CHOICES = [
        (0x0000, 'No Command'),
        (0x9000, 'Note On'),
        (0x8000, 'Note Off'),
        (0xb000, 'Control Change'),
        (0xc000, 'Program Change'),
    ]

    DATA_LABELS = {
        0x9000: 'Note:',
        0x8000: 'Note:',
        0xb000: 'Control:',
        0xc000: 'Program:',
    }

    def __init__(self, *args, **kwargs):
        super(MidiCommandDialog, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        gbsizer = wx.GridBagSizer(8, 8)
        gbsizer.SetCols(2)

        command_label = wx.StaticText(self, wx.ID_ANY, 'Command:')
        gbsizer.Add(command_label, (0, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        command_choice = wx.Choice(self, wx.ID_ANY, choices=[x[1] for x in self.COMMAND_CHOICES])
        self._command_choice = command_choice
        command_value = self.GetValue() & 0xf000
        for n, choice in enumerate(self.COMMAND_CHOICES):
            if choice[0] == command_value:
                command_choice.SetSelection(n)
                break
        self.Bind(wx.EVT_CHOICE, self.OnCommandChoice, command_choice)
        gbsizer.Add(command_choice, (0, 1), (1, 1), wx.ALL, 0)

        channel_label = wx.StaticText(self, wx.ID_ANY, 'Channel:')
        gbsizer.Add(channel_label, (1, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        channel_value = ((self.GetValue() & 0x0f00) >> 16) + 1
        channel_spinner = wx.SpinCtrl(self, wx.ID_ANY, value=str(channel_value), min=1, max=16)
        self._channel_spinner = channel_spinner
        self.Bind(wx.EVT_UPDATE_UI, self.OnChannelUpdate, channel_spinner)
        self.Bind(wx.EVT_TEXT, self.OnChannelSpinner, channel_spinner)
        gbsizer.Add(channel_spinner, (1, 1), (1, 1), wx.ALL, 0)

        data_label_text = self.DATA_LABELS.get(command_value, 'Data:')
        data_label = wx.StaticText(self, wx.ID_ANY, data_label_text, style=wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnDataLabelUpdate, data_label)
        gbsizer.Add(data_label, (2, 0), (1, 1), wx.EXPAND | wx.ALL, 0)
        data_value = self.GetValue() & 0x7f
        data_spinner = MidiNoteSpinCtrl(self, wx.ID_ANY, value=data_value)
        self._data_spinner = data_spinner
        self.Bind(wx.EVT_UPDATE_UI, self.OnDataUpdate, data_spinner)
        self.Bind(wx.EVT_SPINCTRL, self.OnDataSpinner, data_spinner)
        gbsizer.Add(data_spinner, (2, 1), (1, 1), wx.ALL, 0)

        sizer.Add(gbsizer, 1, wx.EXPAND | wx.ALL, 8)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
        self.SetSizerAndFit(sizer)

    def GetValue(self):
        return self._value if hasattr(self, '_value') else 0

    def SetValue(self, value):
        self._value = int(value) & 0xffff
        command_value = self._value & 0xf000
        for n, choice in enumerate(self.COMMAND_CHOICES):
            if choice[0] == command_value:
                self._command_choice.SetSelection(n)
                break
        channel_value = ((self._value & 0x0f00) >> 16) + 1
        self._channel_spinner.SetValue(channel_value)
        data_value = self._value & 0x7f
        self._data_spinner.SetValue(data_value)
        self.UpdateWindowUI()

    def OnCommandChoice(self, event):
        command_choice = event.GetEventObject()
        command_selection = command_choice.GetSelection()
        new_value = (self.GetValue() & 0x0fff) | self.COMMAND_CHOICES[command_selection][0]
        self.SetValue(new_value)

    def OnChannelUpdate(self, event):
        event.Enable(self.GetValue() & 0x8000)

    def OnChannelSpinner(self, event):
        channel_spinner = event.GetEventObject()
        channel_value = channel_spinner.GetValue()
        new_value = (self.GetValue() & 0xf0ff) | (channel_value - 1)
        self.SetValue(new_value)

    def OnDataLabelUpdate(self, event):
        command_value = self.GetValue() & 0xf000
        data_label = event.GetEventObject()
        data_label_text = self.DATA_LABELS.get(command_value, None)
        if data_label_text is not None:
            data_label.SetLabel(data_label_text)

    def OnDataUpdate(self, event):
        event.Enable(self.GetValue() & 0x8000)
        data_spinner = event.GetEventObject()
        command_value = self.GetValue() & 0xf000
        if command_value in (0x8000, 0x9000):
            data_spinner.SetRange(0, 127)
            data_spinner.EnableNotes()
        elif command_value == 0xb000:
            data_spinner.DisableNotes()
            data_spinner.SetRange(0, 120)
        elif command_value == 0xc000:
            data_spinner.DisableNotes()
            data_spinner.SetRange(0, 127)

    def OnDataSpinner(self, event):
        data_spinner = event.GetEventObject()
        data_value = int(data_spinner.GetValue())
        new_value = (self.GetValue() & 0xff00) | (data_value & 0x7f)
        self.SetValue(new_value)
