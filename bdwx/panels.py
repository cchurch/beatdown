# Python
import io

# wxPython
import wx
import wx.html
import wx.lib.agw.pygauge
import wx.lib.agw.peakmeter

# BeatDown
from .constants import *  # noqa
from .controls import *  # noqa
from .dialogs import *  # noqa
from .utils import *  # noqa


class HeaderPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(HeaderPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        logo_data = wx.GetApp().GetResource(1)
        logo_stream = io.BytesIO(logo_data)
        logo_img = wx.Image(logo_stream)
        logo_img.Rescale(48, 48)
        logo_bmp = wx.StaticBitmap(self, -1, logo_img.ConvertToBitmap())
        hsizer.Add(logo_bmp, 0, wx.EXPAND | wx.ALL, 8)

        header_text = wx.StaticText(self, -1, 'BeatDown')
        font = header_text.GetFont()
        font.Scale(2.2)
        font.MakeBold()
        header_text.SetFont(font)
        hsizer.Add(header_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)

        meter_sizer = wx.BoxSizer(wx.VERTICAL)
        meter_sizer.AddStretchSpacer(1)
        input_meter = wx.lib.agw.peakmeter.PeakMeterCtrl(self, ID_INPUT_METER, size=(-1, 32), agwStyle=wx.lib.agw.peakmeter.PM_HORIZONTAL)
        input_meter.SetMeterBands(2, 30)
        input_meter.SetRangeValue(90, 105, 120)
        input_meter.SetBackgroundColour(COLOR_BACKGROUND)
        input_meter.ShowGrid(True)
        meter_sizer.Add(input_meter, 0, wx.EXPAND | wx.LEFT, 32)
        meter_sizer.AddStretchSpacer(1)
        hsizer.Add(meter_sizer, 1, wx.ALL | wx.EXPAND, 4)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(vsizer)


class StatusPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(StatusPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_text = wx.StaticText(self, wx.ID_ANY, '(status)', style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE | wx.ST_ELLIPSIZE_END)
        sizer.Add(status_text, 1, wx.ALL, 4)
        midi_listener_status = wx.StaticBitmap(self, wx.ID_ANY, self.GetStatusBitmap())
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMidiListenerStatus, midi_listener_status)
        sizer.Add(midi_listener_status, 0, wx.ALL, 4)
        midi_dispatcher_status = wx.StaticBitmap(self, wx.ID_ANY, self.GetStatusBitmap())
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMidiDispatcherStatus, midi_dispatcher_status)
        sizer.Add(midi_dispatcher_status, 0, wx.ALL, 4)
        audio_server_status = wx.StaticBitmap(self, wx.ID_ANY, self.GetStatusBitmap())
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateAudioServerStatus, audio_server_status)
        sizer.Add(audio_server_status, 0, wx.ALL, 4)
        sizer.Add((8, 16))
        self.SetSizerAndFit(sizer)

    def GetStatusBitmap(self, art_id='', size=(16, 16)):
        bmp = wx.ArtProvider.GetBitmap(art_id, size=size)
        if not bmp.IsOk():
            bmp = wx.Bitmap(size)
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(COLOR_BACKGROUND))
            dc.Clear()
        return bmp

    def OnUpdateMidiListenerStatus(self, event):
        if not hasattr(self, '_last_midi_listener_status'):
            self._last_midi_listener_status = ''
        new_midi_listener_status = wx.GetApp().GetMidiListenerStatus()
        if new_midi_listener_status != self._last_midi_listener_status:
            tooltip, art_id = {
                'running': ('MIDI Listener Running', wx.ART_INFORMATION),
                'stopped': ('MIDI Listener Stopped', wx.ART_TIP),
                'disabled': ('MIDI Listener Disabled', wx.ART_ERROR),
            }.get(new_midi_listener_status, ('', ''))
            midi_listener_status = event.GetEventObject()
            midi_listener_status.SetToolTip(tooltip)
            midi_listener_status.SetBitmap(self.GetStatusBitmap(art_id))
            self._last_midi_listener_status = new_midi_listener_status

    def OnUpdateMidiDispatcherStatus(self, event):
        if not hasattr(self, '_last_midi_dispatcher_status'):
            self._last_midi_dispatcher_status = ''
        new_midi_dispatcher_status = wx.GetApp().GetMidiDispatcherStatus()
        if new_midi_dispatcher_status != self._last_midi_dispatcher_status:
            tooltip, art_id = {
                'running': ('MIDI Dispatcher Running', wx.ART_INFORMATION),
                'stopped': ('MIDI Dispatcher Stopped', wx.ART_TIP),
                'disabled': ('MIDI Dispatcher Disabled', wx.ART_ERROR),
            }.get(new_midi_dispatcher_status, ('', ''))
            midi_dispatcher_status = event.GetEventObject()
            midi_dispatcher_status.SetToolTip(tooltip)
            midi_dispatcher_status.SetBitmap(self.GetStatusBitmap(art_id))
            self._last_midi_dispatcher_status = new_midi_dispatcher_status

    def OnUpdateAudioServerStatus(self, event):
        if not hasattr(self, '_last_audio_server_status'):
            self._last_audio_server_status = ''
        new_audio_server_status = wx.GetApp().GetAudioServerStatus()
        if new_audio_server_status != self._last_audio_server_status:
            tooltip, art_id = {
                'running': ('Audio Server Running', wx.ART_INFORMATION),
                'stopped': ('Audio Server Stopped', wx.ART_TIP),
                'enabled': ('Audio Server Enabled', wx.ART_WARNING),
                'disabled': ('Audio Server Disabled', wx.ART_ERROR),
            }.get(new_audio_server_status, ('', ''))
            audio_server_status = event.GetEventObject()
            audio_server_status.SetToolTip(tooltip)
            audio_server_status.SetBitmap(self.GetStatusBitmap(art_id))
            self._last_audio_server_status = new_audio_server_status


class SpeedPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(SpeedPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Header with enabled checkbox.
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        header_text = wx.StaticText(self, wx.ID_ANY, 'Speed')
        header_text.SetFont(header_text.GetFont().Scale(1.2).MakeBold())
        header_sizer.Add(header_text, 1, wx.EXPAND | wx.ALL, 0)
        enabled_label = wx.StaticText(self, wx.ID_ANY, 'Enabled:')
        header_sizer.Add(enabled_label, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        enabled_checkbox = wx.CheckBox(self, wx.ID_ANY, '')
        enabled_checkbox.SetValue(wx.GetApp().GetSpeedEnabled())
        self.Bind(wx.EVT_CHECKBOX, self.OnEnabledCheck, enabled_checkbox)
        header_sizer.Add(enabled_checkbox, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 4)

        # Spacer.
        spacer_panel = wx.Panel(self, wx.ID_ANY)
        spacer_panel.SetMinSize((-1, 2))
        spacer_panel.SetBackgroundColour(COLOR_LINES)
        sizer.Add(spacer_panel, 0, wx.EXPAND | wx.ALL, 4)

        # Sizer for controls.
        gbsizer = wx.GridBagSizer(8, 8)
        gbsizer.SetCols(2)
        gbsizer.AddGrowableCol(0)
        gbsizer.AddGrowableCol(1)

        # BPM settings.
        bpm_label = wx.StaticText(self, wx.ID_ANY, 'BPM:')
        gbsizer.Add(bpm_label, (0, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        bpm_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bpm_value = str(wx.GetApp().GetSpeedBPM())
        bpm_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(80, -1), value=bpm_value, min=40, max=480)
        self.Bind(wx.EVT_TEXT, self.OnBPMSpinner, bpm_spinner)
        bpm_sizer.Add(bpm_spinner, 0, wx.ALL, 0)
        gbsizer.Add(bpm_sizer, (0, 1), (1, 1), wx.ALL, 0)

        # Beat Indicator.
        beat_display = BeatDisplay(self, ID_SPEED_DISPLAY, size=(-1, 30))
        beat_display.SetValue(50)
        beat_display.SetForegroundColour(wx.GREEN)
        beat_display.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        gbsizer.Add(beat_display, (1, 1), (1, 1), wx.EXPAND | wx.ALL, 1)

        sizer.Add(gbsizer, 1, wx.EXPAND | wx.ALL, 8)
        self.SetSizerAndFit(sizer)

    def OnEnabledCheck(self, event):
        wx.GetApp().SetSpeedEnabled(event.IsChecked())

    def OnEnabledUpdate(self, event):
        event.Enable(wx.GetApp().GetSpeedEnabled())

    def OnBPMSpinner(self, event):
        wx.GetApp().SetSpeedBPM(event.GetEventObject().GetValue())


class StrengthPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(StrengthPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Header with enabled checkbox.
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        header_text = wx.StaticText(self, wx.ID_ANY, 'Strength')
        header_text.SetFont(header_text.GetFont().Scale(1.2).MakeBold())
        header_sizer.Add(header_text, 1, wx.EXPAND | wx.ALL, 0)
        enabled_label = wx.StaticText(self, wx.ID_ANY, 'Enabled:')
        header_sizer.Add(enabled_label, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        enabled_checkbox = wx.CheckBox(self, wx.ID_ANY, '')
        enabled_checkbox.SetValue(wx.GetApp().GetStrengthEnabled())
        self.Bind(wx.EVT_CHECKBOX, self.OnEnabledCheck, enabled_checkbox)
        header_sizer.Add(enabled_checkbox, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 4)

        # Spacer.
        spacer_panel = wx.Panel(self, wx.ID_ANY)
        spacer_panel.SetMinSize((-1, 2))
        spacer_panel.SetBackgroundColour(COLOR_LINES)
        sizer.Add(spacer_panel, 0, wx.EXPAND | wx.ALL, 4)

        # Sizer for controls.
        gbsizer = wx.GridBagSizer(8, 8)
        gbsizer.SetCols(2)
        gbsizer.AddGrowableCol(0)
        gbsizer.AddGrowableCol(1)

        # LPF settings.
        lpf_label = wx.StaticText(self, wx.ID_ANY, 'LPF:')
        gbsizer.Add(lpf_label, (0, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        lpf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lpf_value = str(wx.GetApp().GetStrengthLPF())
        lpf_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(80, -1), value=lpf_value, min=20, max=2000)
        self.Bind(wx.EVT_TEXT, self.OnLPFSpinner, lpf_spinner)
        lpf_sizer.Add(lpf_spinner, 0, wx.ALL, 0)
        lpf_hz_label = wx.StaticText(self, wx.ID_ANY, 'Hz')
        lpf_sizer.Add(lpf_hz_label, 0, wx.LEFT, 4)
        gbsizer.Add(lpf_sizer, (0, 1), (1, 1), wx.ALL, 0)

        # Attack settings (rise time of follower).
        attack_label = wx.StaticText(self, wx.ID_ANY, 'Attack:')
        gbsizer.Add(attack_label, (1, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        attack_sizer = wx.BoxSizer(wx.HORIZONTAL)
        attack_value = wx.GetApp().GetStrengthAttack()
        attack_spinner = wx.SpinCtrlDouble(self, wx.ID_ANY, size=(80, -1), value=str(attack_value), min=0.0, max=10.0, inc=0.1)
        attack_spinner.SetDigits(3)
        attack_spinner.SetValue(attack_value)
        # self.Bind(wx.EVT_SPINCTRL, self.OnAttackSpinner, attack_spinner)
        self.Bind(wx.EVT_TEXT, self.OnAttackSpinner, attack_spinner)
        attack_sizer.Add(attack_spinner, 0, wx.ALL, 0)
        attack_seconds_label = wx.StaticText(self, wx.ID_ANY, 'sec')
        attack_sizer.Add(attack_seconds_label, 0, wx.LEFT, 4)
        gbsizer.Add(attack_sizer, (1, 1), (1, 1), wx.ALL, 0)

        # Release settings (fall time of follower).
        release_label = wx.StaticText(self, wx.ID_ANY, 'Release:')
        gbsizer.Add(release_label, (2, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        release_sizer = wx.BoxSizer(wx.HORIZONTAL)
        release_value = str(wx.GetApp().GetStrengthRelease())
        release_spinner = wx.SpinCtrlDouble(self, wx.ID_ANY, size=(80, -1), value=release_value, min=0.0, max=10.0, inc=0.1)
        release_spinner.SetDigits(3)
        self.Bind(wx.EVT_TEXT, self.OnReleaseSpinner, release_spinner)
        release_sizer.Add(release_spinner, 0, wx.ALL, 0)
        release_seconds_label = wx.StaticText(self, wx.ID_ANY, 'sec')
        release_sizer.Add(release_seconds_label, 0, wx.LEFT, 4)
        gbsizer.Add(release_sizer, (2, 1), (1, 1), wx.ALL, 0)

        # Min SPL to velocity association.
        min_label = wx.StaticText(self, wx.ID_ANY, 'Minimum:')
        gbsizer.Add(min_label, (3, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        min_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_spl_value = str(wx.GetApp().GetStrengthMinSPL())
        min_spl_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(70, -1), value=min_spl_value, min=-120, max=0)
        self.Bind(wx.EVT_TEXT, self.OnMinSPLSpinner, min_spl_spinner)
        min_sizer.Add(min_spl_spinner, 0, wx.ALL, 0)
        min_spl_label = wx.StaticText(self, wx.ID_ANY, 'dB =')
        min_sizer.Add(min_spl_label, 0, wx.LEFT | wx.RIGHT, 4)
        min_velo_value = str(wx.GetApp().GetStrengthMinVelocity())
        min_velo_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1), value=min_velo_value, min=0, max=127)
        self.Bind(wx.EVT_TEXT, self.OnMinVelocitySpinner, min_velo_spinner)
        min_sizer.Add(min_velo_spinner, 0, wx.ALL, 0)
        gbsizer.Add(min_sizer, (3, 1), (1, 1), wx.ALL, 0)

        # Max SPL to velocity association.
        max_label = wx.StaticText(self, wx.ID_ANY, 'Maximum:')
        gbsizer.Add(max_label, (4, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        max_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_spl_value = str(wx.GetApp().GetStrengthMaxSPL())
        max_spl_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(70, -1), value=max_spl_value, min=-120, max=0)
        self.Bind(wx.EVT_TEXT, self.OnMaxSPLSpinner, max_spl_spinner)
        max_sizer.Add(max_spl_spinner, 0, wx.ALL, 0)
        max_spl_label = wx.StaticText(self, wx.ID_ANY, 'dB =')
        max_sizer.Add(max_spl_label, 0, wx.LEFT | wx.RIGHT, 4)
        max_velo_value = str(wx.GetApp().GetStrengthMaxVelocity())
        max_velo_spinner = wx.SpinCtrl(self, wx.ID_ANY, size=(60, -1), value=max_velo_value, min=0, max=127)
        self.Bind(wx.EVT_TEXT, self.OnMaxVelocitySpinner, max_velo_spinner)
        max_sizer.Add(max_velo_spinner, 0, wx.ALL, 0)
        gbsizer.Add(max_sizer, (4, 1), (1, 1), wx.ALL, 0)

        # MIDI output selection.
        midi_label = wx.StaticText(self, wx.ID_ANY, 'MIDI Out:')
        gbsizer.Add(midi_label, (5, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT, 0)
        midi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        midi_text = wx.TextCtrl(self, wx.ID_ANY, value='', style=wx.TE_READONLY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnMidiTextUpdate, midi_text)
        midi_sizer.Add(midi_text, 0, wx.ALL, 0)
        midi_button = wx.Button(self, wx.ID_ANY, '...', style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnMidiButton, midi_button)
        midi_sizer.Add(midi_button, 0, wx.LEFT, 4)
        gbsizer.Add(midi_sizer, (5, 1), (1, 1), wx.ALL, 0)

        # Stregth gauge to show current velocity.
        strength_gauge = wx.lib.agw.pygauge.PyGauge(self, ID_STRENGTH_GAUGE, size=(-1, 10), style=wx.GA_HORIZONTAL)
        strength_gauge.SetRange(127)
        strength_gauge.SetValue(50)
        strength_gauge.SetBarColor(wx.GREEN)
        strength_gauge.SetBackgroundColour(wx.WHITE)
        strength_gauge.SetBorderColor(wx.BLACK)
        gbsizer.Add(strength_gauge, (6, 1), (1, 1), wx.EXPAND | wx.ALL, 0)

        sizer.Add(gbsizer, 1, wx.EXPAND | wx.ALL, 8)
        self.SetSizerAndFit(sizer)

    def OnEnabledCheck(self, event):
        wx.GetApp().SetStrengthEnabled(event.IsChecked())

    def OnEnabledUpdate(self, event):
        event.Enable(wx.GetApp().GetStrengthEnabled())

    def OnLPFSpinner(self, event):
        wx.GetApp().SetStrengthLPF(event.GetEventObject().GetValue())

    def OnAttackSpinner(self, event):
        wx.GetApp().SetStrengthAttack(event.GetEventObject().GetValue())

    def OnReleaseSpinner(self, event):
        wx.GetApp().SetStrengthRelease(event.GetEventObject().GetValue())

    def OnMinSPLSpinner(self, event):
        wx.GetApp().SetStrengthMinSPL(event.GetEventObject().GetValue())

    def OnMinVelocitySpinner(self, event):
        wx.GetApp().SetStrengthMinVelocity(event.GetEventObject().GetValue())

    def OnMaxSPLSpinner(self, event):
        wx.GetApp().SetStrengthMaxSPL(event.GetEventObject().GetValue())

    def OnMaxVelocitySpinner(self, event):
        wx.GetApp().SetStrengthMaxVelocity(event.GetEventObject().GetValue())

    def OnMidiButton(self, event):
        dialog = MidiCommandDialog(self, wx.ID_ANY, 'MIDI Output')
        dialog.SetValue(wx.GetApp().GetStrengthMidiOutput())
        dialog.CenterOnScreen()
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            wx.GetApp().SetStrengthMidiOutput(dialog.GetValue())
        dialog.Destroy()

    def OnMidiTextUpdate(self, event):
        midi_output = wx.GetApp().GetStrengthMidiOutput()
        command = midi_output & 0xf000
        channel = ((midi_output & 0x0f00) >> 16) + 1
        data = midi_output & 0x7f
        if command == 0x9000:
            value = 'Ch{} {} On'.format(channel, int_to_midi_note(data))
        elif command == 0x8000:
            value = 'Ch{} {} Off'.format(channel, int_to_midi_note(data))
        elif command == 0xb000:
            value = 'Ch{} CC {}'.format(channel, data)
        elif command == 0xc000:
            value = 'Ch{} PC {}'.format(channel, data)
        else:
            value = ''
        midi_text = event.GetEventObject()
        midi_text.SetValue(value)


class StylePanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(StylePanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        header_text = wx.StaticText(self, wx.ID_ANY, 'Style')
        header_text.SetFont(header_text.GetFont().Scale(1.2).MakeBold())
        header_sizer.Add(header_text, 1, wx.EXPAND | wx.ALL, 0)
        enabled_label = wx.StaticText(self, wx.ID_ANY, 'Enabled:')
        header_sizer.Add(enabled_label, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        enabled_checkbox = wx.CheckBox(self, wx.ID_ANY, '')
        header_sizer.Add(enabled_checkbox, 0, wx.ALIGN_BOTTOM | wx.LEFT, 4)
        sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 4)

        # Spacer.
        spacer_panel = wx.Panel(self, wx.ID_ANY)
        spacer_panel.SetMinSize((-1, 2))
        spacer_panel.SetBackgroundColour(COLOR_LINES)
        sizer.Add(spacer_panel, 0, wx.EXPAND | wx.ALL, 4)

        sizer.AddStretchSpacer(1)
        self.SetSizerAndFit(sizer)


class SetupPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(SetupPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_BACKGROUND)
        self.SetForegroundColour(COLOR_FOREGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        header_text = wx.StaticText(self, wx.ID_ANY, 'Setup')
        header_text.SetFont(header_text.GetFont().Scale(1.2).MakeBold())
        sizer.Add(header_text, 0, wx.EXPAND | wx.ALL, 4)

        wx.GetApp().RefreshAudioMidiIO()  # FIXME: Do periodically?

        gbsizer = wx.GridBagSizer(8, 8)
        gbsizer.SetCols(4)
        gbsizer.AddGrowableCol(0)
        gbsizer.AddGrowableCol(2)

        # Label for audio input selection.
        audio_input_label = wx.StaticText(self, wx.ID_ANY, 'Audio Input:')
        gbsizer.Add(audio_input_label, (0, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        # Dropdown select for audio input source.
        audio_input_choices = self.GetAudioInputChoices()
        audio_input_select = wx.Choice(self, wx.ID_ANY, choices=[x[1] for x in audio_input_choices])
        audio_input_selection = self.GetAudioInputSelection()
        audio_input_select.SetSelection(audio_input_selection)
        self.Bind(wx.EVT_CHOICE, self.OnChangeAudioInputSelect, audio_input_select)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateAudioInputSelect, audio_input_select)
        gbsizer.Add(audio_input_select, (0, 1), (1, 1), wx.TOP | wx.EXPAND, 0)

        # Label for audio channel selection.
        audio_channels_label = wx.StaticText(self, -1, 'Channels:')
        gbsizer.Add(audio_channels_label, (1, 0), (1, 1), wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        # Row of checkboxes for audio channel selection.
        grid_sizer = wx.GridSizer(2, 0, 0, 0)
        audio_input_channels_selection = self.GetAudioInputChannelsSelection()
        for n in range(8):
            check_box = wx.CheckBox(self, wx.ID_ANY, name='accb_{}'.format(n))
            if n in audio_input_channels_selection:
                check_box.SetValue(True)
            grid_sizer.Add(check_box, 1, wx.ALIGN_CENTER | wx.ALL, 0)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateAudioInputChannel, check_box)
            self.Bind(wx.EVT_CHECKBOX, self.OnCheckAudioInputChannel, check_box)
        for n in range(8):
            static_text = wx.StaticText(self, wx.ID_ANY, '{} '.format(n + 1), name='aclb_{}'.format(n))
            static_text.SetFont(static_text.GetFont().MakeSmaller())
            grid_sizer.Add(static_text, 1, wx.ALIGN_CENTER | wx.ALL, 0)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateAudioInputChannel, static_text)
        gbsizer.Add(grid_sizer, (1, 1), (1, 1), wx.TOP | wx.EXPAND, 0)

        # Label for midi input selection.
        midi_input_label = wx.StaticText(self, -1, 'MIDI Input:')
        gbsizer.Add(midi_input_label, (0, 2), (1, 1), wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        # Dropdown select for midi input source.
        midi_input_choices = self.GetMidiInputChoices()
        midi_input_select = wx.Choice(self, wx.ID_ANY, choices=[x[1] for x in midi_input_choices])
        midi_input_selection = self.GetMidiInputSelection()
        midi_input_select.SetSelection(midi_input_selection)
        self.Bind(wx.EVT_CHOICE, self.OnChangeMidiInputSelect, midi_input_select)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMidiInputSelect, midi_input_select)
        gbsizer.Add(midi_input_select, (0, 3), (1, 1), wx.TOP | wx.EXPAND, 0)

        # Label for midi output selection.
        midi_output_label = wx.StaticText(self, -1, 'MIDI Output:')
        gbsizer.Add(midi_output_label, (1, 2), (1, 1), wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        # Dropdown select for midi output device.
        midi_output_choices = self.GetMidiOutputChoices()
        midi_output_select = wx.Choice(self, wx.ID_ANY, choices=[x[1] for x in midi_output_choices])
        midi_output_selection = self.GetMidiOutputSelection()
        midi_output_select.SetSelection(midi_output_selection)
        self.Bind(wx.EVT_CHOICE, self.OnChangeMidiOutputSelect, midi_output_select)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMidiOutputSelect, midi_output_select)
        gbsizer.Add(midi_output_select, (1, 3), (1, 1), wx.TOP | wx.EXPAND, 0)

        sizer.Add(gbsizer, 1, wx.ALIGN_CENTER | wx.ALL, 8)
        self.SetSizerAndFit(sizer)

    def GetAudioInputChoices(self):
        audio_inputs = wx.GetApp().GetAudioInputs()
        choices = [(-1, '(No Audio Input)')]
        for input_index, input_details in sorted(audio_inputs.items()):
            input_default = 'default, ' if input_details['default'] else ''
            input_label = '{name} ({0}{channels}ch)'.format(input_default, **input_details)
            choices.append((input_index, input_label))
        return choices

    def GetAudioInputSelection(self):
        audio_input = wx.GetApp().GetAudioInput()
        if audio_input == -1:
            return 0
        audio_inputs = wx.GetApp().GetAudioInputs()
        audio_input_selection = wx.NOT_FOUND
        for n, (input_index, input_details) in enumerate(sorted(audio_inputs.items())):
            if input_index == audio_input or (input_details['default'] and audio_input < 0):
                audio_input_selection = n + 1
                break
            elif input_details['default']:
                audio_input_selection = n + 1
        return audio_input_selection

    def SetAudioInputSelection(self, audio_input_selection=-1):
        if audio_input_selection == 0:
            wx.GetApp().SetAudioInput(-1)
            return
        audio_inputs = wx.GetApp().GetAudioInputs()
        audio_input = wx.GetApp().GetAudioInput()
        for n, (input_index, input_details) in enumerate(sorted(audio_inputs.items())):
            if (n + 1) == audio_input_selection and input_index != audio_input:
                wx.GetApp().SetAudioInput(input_index)

    def OnChangeAudioInputSelect(self, event):
        audio_input_select = event.GetEventObject()
        audio_input_selection = audio_input_select.GetSelection()
        self.SetAudioInputSelection(audio_input_selection)
        # if not self.GetAudioInputChannelsSelection():
        #     self.SetAudioInputChannelsSelection(range(self.GetAudioInputMaxChannels()))

    def OnUpdateAudioInputSelect(self, event):
        event.Enable(self.GetAudioInputSelection() != wx.NOT_FOUND)

    def GetAudioInputMaxChannels(self):
        audio_inputs = wx.GetApp().GetAudioInputs()
        audio_input = wx.GetApp().GetAudioInput()
        for input_index, input_details in audio_inputs.items():
            if input_index == audio_input:
                return min(8, input_details['channels'])
        return -1

    def GetAudioInputChannelsSelection(self):
        audio_input_channels = wx.GetApp().GetAudioInputChannels()
        selected_channels = set()
        for n in range(self.GetAudioInputMaxChannels()):
            if audio_input_channels >= 0 and audio_input_channels & (2 ** n):
                selected_channels.add(n)
        return selected_channels

    def SetAudioInputChannelsSelection(self, selected_channels):
        previous_audio_input_channels = wx.GetApp().GetAudioInputChannels()
        audio_input_channels = 0
        for n in range(self.GetAudioInputMaxChannels()):
            if n in selected_channels:
                audio_input_channels |= (2 ** n)
        if audio_input_channels != previous_audio_input_channels:
            wx.GetApp().SetAudioInputChannels(audio_input_channels)

    def OnCheckAudioInputChannel(self, event):
        input_name = event.GetEventObject().GetName()
        input_index = int(input_name.split('_')[-1])
        selected_channels = self.GetAudioInputChannelsSelection()
        if event.IsChecked():
            selected_channels.add(input_index)
        else:
            selected_channels.discard(input_index)
        self.SetAudioInputChannelsSelection(selected_channels)

    def OnUpdateAudioInputChannel(self, event):
        input_name = event.GetEventObject().GetName()
        if input_name.startswith('accb_'):
            event.Enable(self.GetAudioInputSelection() not in (0, wx.NOT_FOUND))
        input_index = int(input_name.split('_')[-1])
        max_channels = self.GetAudioInputMaxChannels()
        event.Show(input_index < max_channels or max_channels < 0)

    def GetMidiInputChoices(self):
        midi_inputs = wx.GetApp().GetMidiInputs()
        choices = [(-1, '(No MIDI Input)')]
        for input_index, input_details in sorted(midi_inputs.items()):
            input_default = ' (default)' if input_details['default'] else ''
            input_label = '{name}{0}'.format(input_default, **input_details)
            choices.append((input_index, input_label))
        return choices

    def GetMidiInputSelection(self):
        midi_input = wx.GetApp().GetMidiInput()
        if midi_input == -1:
            return 0
        midi_inputs = wx.GetApp().GetMidiInputs()
        midi_input_selection = wx.NOT_FOUND
        for n, (input_index, input_details) in enumerate(sorted(midi_inputs.items())):
            if input_index == midi_input or (input_details['default'] and midi_input < 0):
                midi_input_selection = n + 1
                break
            elif input_details['default']:
                midi_input_selection = n + 1
        return midi_input_selection

    def SetMidiInputSelection(self, midi_input_selection=-1):
        if midi_input_selection == 0:
            wx.GetApp().SetMidiInput(-1)
            return
        midi_inputs = wx.GetApp().GetMidiInputs()
        midi_input = wx.GetApp().GetMidiInput()
        for n, (input_index, input_details) in enumerate(sorted(midi_inputs.items())):
            if (n + 1) == midi_input_selection and input_index != midi_input:
                wx.GetApp().SetMidiInput(input_index)

    def OnChangeMidiInputSelect(self, event):
        midi_input_select = event.GetEventObject()
        midi_input_selection = midi_input_select.GetSelection()
        self.SetMidiInputSelection(midi_input_selection)

    def OnUpdateMidiInputSelect(self, event):
        event.Enable(self.GetMidiInputSelection() != wx.NOT_FOUND)

    def GetMidiOutputChoices(self):
        midi_outputs = wx.GetApp().GetMidiOutputs()
        choices = [(-1, '(No MIDI Output)')]
        for output_index, output_details in sorted(midi_outputs.items()):
            output_default = ' (default)' if output_details['default'] else ''
            output_label = '{name}{0}'.format(output_default, **output_details)
            choices.append((output_index, output_label))
        return choices

    def GetMidiOutputSelection(self):
        midi_output = wx.GetApp().GetMidiOutput()
        if midi_output == -1:
            return 0
        midi_outputs = wx.GetApp().GetMidiOutputs()
        midi_output_selection = wx.NOT_FOUND
        for n, (output_index, output_details) in enumerate(sorted(midi_outputs.items())):
            if output_index == midi_output or (output_details['default'] and midi_output < 0):
                midi_output_selection = n + 1
                break
            elif output_details['default']:
                midi_output_selection = n + 1
        return midi_output_selection

    def SetMidiOutputSelection(self, midi_output_selection=-1):
        if midi_output_selection == 0:
            wx.GetApp().SetMidiOutput(-1)
            return
        midi_outputs = wx.GetApp().GetMidiOutputs()
        midi_output = wx.GetApp().GetMidiOutput()
        for n, (output_index, output_details) in enumerate(sorted(midi_outputs.items())):
            if (n + 1) == midi_output_selection and output_index != midi_output:
                wx.GetApp().SetMidiOutput(output_index)

    def OnChangeMidiOutputSelect(self, event):
        midi_output_select = event.GetEventObject()
        midi_output_selection = midi_output_select.GetSelection()
        self.SetMidiOutputSelection(midi_output_selection)

    def OnUpdateMidiOutputSelect(self, event):
        event.Enable(self.GetMidiOutputSelection() != wx.NOT_FOUND)


class ContentPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(ContentPanel, self).__init__(*args, **kwargs)
        self.SetBackgroundColour(COLOR_LINES)
        self.SetForegroundColour(COLOR_FOREGROUND)
        vsizer = wx.BoxSizer(wx.VERTICAL)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_panel = SpeedPanel(self, wx.ID_ANY)
        hsizer.Add(speed_panel, 1, wx.EXPAND | wx.ALL, 4)
        strength_panel = StrengthPanel(self, wx.ID_ANY)
        hsizer.Add(strength_panel, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 4)
        style_panel = StylePanel(self, wx.ID_ANY)
        hsizer.Add(style_panel, 1, wx.EXPAND | wx.ALL, 4)
        vsizer.Add(hsizer, 1, wx.EXPAND, 4)

        setup_panel = SetupPanel(self, wx.ID_ANY)
        vsizer.Add(setup_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        self.SetSizerAndFit(vsizer)


class MainPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(MainPanel, self).__init__(*args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        header_panel = HeaderPanel(self)
        sizer.Add(header_panel, 0, wx.EXPAND | wx.ALL, 0)
        content_panel = ContentPanel(self)
        sizer.Add(content_panel, 1, wx.EXPAND | wx.ALL, 0)
        status_panel = StatusPanel(self)
        sizer.Add(status_panel, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(sizer)
        self.SetBackgroundColour(wx.Colour(0x20, 0x20, 0x20))
