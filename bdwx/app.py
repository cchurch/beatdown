# Python
import logging
import math
import optparse
import os
import socket
import sys
import textwrap
import time
import weakref

# wxPython
import wx

# PyWin32
try:
    import win32api
    import win32con
    import win32gui
except ImportError:
    win32api, win32con, win32gui = None, None, None

# PyO
import pyo

# BeatDown
from .constants import *  # noqa
from .frames import *  # noqa
from .engine import *  # noqa


class OptionParser(optparse.OptionParser):
    """Custom option parse that displays help and errors with a wxMessageBox."""

    def print_help(self, file=None):
        """Display the program help."""
        wx.MessageBox(self.format_help(), APP_NAME, wx.OK | wx.ICON_QUESTION)

    def print_usage(self, file=None):
        """Skip displaying the usage information (include it in error instead)."""

    def print_version(self):
        """Display the current application version."""
        msg = 'Current version:\n\n%s' % self.get_version()
        wx.MessageBox(msg, APP_NAME, wx.OK | wx.ICON_INFORMATION)

    def error(self, msg):
        """Display an error message."""
        msg = '%s\n\n%s' % (msg, self.format_help())
        wx.MessageBox(msg, APP_NAME, wx.OK | wx.ICON_ERROR)
        self.exit()

    def exit(self):
        """Trigger the wxApp to exit."""
        raise optparse.OptParseError('exit')


# class Log(wx.PyLog):

#     def __init__(self, *args, **kwargs):
#         super(Log, self).__init__(*args, **kwargs)

#     def DoLogRecord(self, level, msg, info):
#         top_window = wx.GetApp().GetTopWindow()
#         if top_window:
#             output_panel = top_window.FindWindowById(ID_OUTPUT_PANEL)
#         else:
#             output_panel = None

#         if output_panel:
#             output_panel.LogRecord(level, msg, info.timestamp)


class App(wx.App):
    """Main application instance."""

    def OnInit(self):
        parser = OptionParser(version='0.1.0')
        try:
            options, args = parser.parse_args()
        except optparse.OptParseError:
            return False
        frame_title = self.GetTitle()
        frame_userdata = 0xBEA1D0
        self.SetVendorName(VENDOR_NAME)
        self.SetAppName(APP_NAME)
        self.sic = wx.SingleInstanceChecker(self.GetAppName())
        if self.sic.IsAnotherRunning():
            if win32gui:
                other_hwnds = []

                def enum_windows_callback(hwnd, extra):
                    if win32gui.GetWindowText(hwnd) != frame_title:
                        return
                    hwnd_userdata = win32gui.GetWindowLong(hwnd, win32con.GWL_USERDATA)
                    if hwnd_userdata != frame_userdata:
                        return
                    extra.append(hwnd)
                win32gui.EnumWindows(enum_windows_callback, other_hwnds)
                other_hwnd = other_hwnds[0] if other_hwnds else None
                if other_hwnd:
                    win32gui.PostMessage(other_hwnd, win32con.WM_USER, 0, 1)
            self.ExitMainLoop()
            return True

        self.RebootAudioServer()
        self.RebootMidiListener()
        self.RebootMidiDispatcher()
        # wx.Log.SetActiveTarget(Log())
        # wx.Log.SetVerbose()
        # self.SetLogLevel()
        frame = Frame(None, wx.ID_ANY, frame_title)
        if win32gui:
            win32gui.SetWindowLong(frame.GetHandle(), win32con.GWL_USERDATA, frame_userdata)
        frame.Show()
        # wx.LogError('error')
        # wx.LogWarning('warning')
        # wx.LogMessage('--- %s %s ---' % (APP_NAME, VERSION))
        # wx.LogStatus('status')
        # wx.LogVerbose('verbose')
        # wx.LogDebug('debug')
        wx.UpdateUIEvent.SetUpdateInterval(50)
        self.Bind(EVT_AUDIO_SERVER_STARTED, self.OnAudioServerStarted)
        self.Bind(EVT_AUDIO_SERVER_STOPPED, self.OnAudioServerStopped)

        return True

    def OnExit(self):
        del self.sic
        self.ShutdownAudioServer()
        return True

    def GetAppPath(self):
        return APP_PATH

    def GetIconPath(self):
        return ICON_PATH

    def GetVersion(self):
        return VERSION

    def GetTitle(self):
        return APP_NAME

    def GetSetting(self, name, type_=str, default=''):
        if not hasattr(self, '_%s_' % name):
            getter = {
                bool: wx.Config.Get().ReadBool,
                int: wx.Config.Get().ReadInt,
                float: wx.Config.Get().ReadFloat,
            }.get(type_, wx.Config.Get().Read)
            setattr(self, '_%s_' % name, type_(getter(name, default)))
        return getattr(self, '_%s_' % name)

    def SetSetting(self, name, type_=str, value=''):
        setattr(self, '_%s_' % name, type_(value))
        setter = {
            bool: wx.Config.Get().WriteBool,
            int: wx.Config.Get().WriteInt,
            float: wx.Config.Get().WriteFloat,
        }.get(type_, wx.Config.Get().Write)
        setter(name, type_(value))
        win = self.GetTopWindow()
        if win:
            win.UpdateWindowUI()
        wx.Config.Get().Flush()

    GetMaximized = lambda s: s.GetSetting('maximized', bool, False)
    SetMaximized = lambda s, v: s.SetSetting('maximized', bool, v)
    GetLeft = lambda s: s.GetSetting('left', int, -999999)
    SetLeft = lambda s, v: s.SetSetting('left', int, v)
    GetTop = lambda s: s.GetSetting('top', int, -999999)
    SetTop = lambda s, v: s.SetSetting('top', int, v)
    GetWidth = lambda s: s.GetSetting('width', int, -1)
    SetWidth = lambda s, v: s.SetSetting('width', int, v)
    GetHeight = lambda s: s.GetSetting('height', int, -1)
    SetHeight = lambda s, v: s.SetSetting('height', int, v)

    def SetAudioSetting(self, name, type_=str, value=''):
        self.SetSetting(name, type_, value)
        if name == 'audio_input_channels':
            self.UpdateAudioStrengthAnalyzer()
        else:
            self.RebootAudioServer()

    # Device index as returned from pyo.pa_get_input_devices().
    GetAudioInput = lambda s: s.GetSetting('audio_input', int, -1)
    SetAudioInput = lambda s, v: s.SetAudioSetting('audio_input', int, v)

    # Bitmask of selected audio input channels.
    GetAudioInputChannels = lambda s: s.GetSetting('audio_input_channels', int, -1)
    SetAudioInputChannels = lambda s, v: s.SetAudioSetting('audio_input_channels', int, v)

    def SetMidiInputSetting(self, name, type_=str, value=''):
        self.SetSetting(name, type_, value)
        self.RebootMidiListener()

    # Device index as returned from pyo.pm_get_input_devices().
    GetMidiInput = lambda s: s.GetSetting('midi_input', int, -1)
    SetMidiInput = lambda s, v: s.SetMidiInputSetting('midi_input', int, v)

    def SetMidiOutputSetting(self, name, type_=str, value=''):
        self.SetSetting(name, type_, value)
        self.RebootMidiDispatcher()

    # Device index as returned from pyo.pm_get_output_devices().
    GetMidiOutput = lambda s: s.GetSetting('midi_output', int, -1)
    SetMidiOutput = lambda s, v: s.SetMidiOutputSetting('midi_output', int, v)

    # "Speed" settings (beat clock based on attack and beat detection).
    GetSpeedEnabled = lambda s: s.GetSetting('speed_enabled', bool, False)
    SetSpeedEnabled = lambda s, v: s.SetSetting('speed_enabled', bool, v)

    # "Strength" settings (velocity output based on sound level).
    def SetStrengthSetting(self, name, type_=str, value=''):
        self.SetSetting(name, type_, value)
        self.UpdateAudioStrengthAnalyzer()

    GetStrengthEnabled = lambda s: s.GetSetting('strength_enabled', bool, False)
    SetStrengthEnabled = lambda s, v: s.SetStrengthSetting('strength_enabled', bool, v)
    GetStrengthLPF = lambda s: s.GetSetting('strength_lpf', int, 120)
    SetStrengthLPF = lambda s, v: s.SetStrengthSetting('strength_lpf', int, v)
    GetStrengthAttack = lambda s: s.GetSetting('strength_attack', float, 0.1)
    SetStrengthAttack = lambda s, v: s.SetStrengthSetting('strength_attack', float, v)
    GetStrengthRelease = lambda s: s.GetSetting('strength_release', float, 0.1)
    SetStrengthRelease = lambda s, v: s.SetStrengthSetting('strength_release', float, v)
    GetStrengthMinSPL = lambda s: s.GetSetting('strength_min_spl', int, -120)
    SetStrengthMinSPL = lambda s, v: s.SetStrengthSetting('strength_min_spl', int, v)
    GetStrengthMinVelocity = lambda s: s.GetSetting('strength_min_velocity', int, 0)
    SetStrengthMinVelocity = lambda s, v: s.SetStrengthSetting('strength_min_velocity', int, v)
    GetStrengthMaxSPL = lambda s: s.GetSetting('strength_max_spl', int, 0)
    SetStrengthMaxSPL = lambda s, v: s.SetStrengthSetting('strength_max_spl', int, v)
    GetStrengthMaxVelocity = lambda s: s.GetSetting('strength_max_velocity', int, 127)
    SetStrengthMaxVelocity = lambda s, v: s.SetStrengthSetting('strength_max_velocity', int, v)
    GetStrengthMidiOutput = lambda s: s.GetSetting('strength_midi_output', int, 0)
    SetStrengthMidiOutput = lambda s, v: s.SetStrengthSetting('strength_midi_output', int, v)

    # "Style" settings (Note/control outputs based on pitch/frequency).
    GetStyleEnabled = lambda s: s.GetSetting('style_enabled', bool, False)
    SetStyleEnabled = lambda s, v: s.SetSetting('style_enabled', bool, v)

    def GetAudioInputs(self):
        if not hasattr(self, '_audio_inputs'):
            input_device_names, input_device_indexes = pyo.pa_get_input_devices()
            default_input_index = pyo.pa_get_default_input()
            audio_inputs = {}
            for input_index, input_name in zip(input_device_indexes, input_device_names):
                input_max_channels = pyo.pa_get_input_max_channels(input_index)
                if 'logmein' in input_name.lower():
                    input_max_channels = 16
                audio_inputs[input_index] = {
                    'name': input_name,
                    'default': bool(input_index == default_input_index),
                    'channels': input_max_channels,
                }
            setattr(self, '_audio_inputs', audio_inputs)
        return getattr(self, '_audio_inputs')

    def RefreshAudioInputs(self):
        if hasattr(self, '_audio_inputs'):
            delattr(self, '_audio_inputs')

    def GetAudioOutputs(self):
        if not hasattr(self, '_audio_outputs'):
            output_device_names, output_device_indexes = pyo.pa_get_output_devices()
            default_output_index = pyo.pa_get_default_output()
            audio_outputs = {}
            for output_index, output_name in zip(output_device_indexes, output_device_names):
                output_max_channels = pyo.pa_get_output_max_channels(output_index)
                audio_outputs[output_index] = {
                    'name': output_name,
                    'default': bool(output_index == default_output_index),
                    'channels': output_max_channels,
                }
            setattr(self, '_audio_outputs', audio_outputs)
        return getattr(self, '_audio_outputs')

    def RefreshAudioOutputs(self):
        if hasattr(self, '_audio_outputs'):
            delattr(self, '_audio_outputs')

    def GetMidiInputs(self):
        if not hasattr(self, '_midi_inputs'):
            input_device_names, input_device_indexes = pyo.pm_get_input_devices()
            default_input_index = pyo.pm_get_default_input()
            midi_inputs = {}
            for input_index, input_name in zip(input_device_indexes, input_device_names):
                midi_inputs[input_index] = {
                    'name': input_name,
                    'default': bool(input_index == default_input_index),
                }
            setattr(self, '_midi_inputs', midi_inputs)
        return getattr(self, '_midi_inputs')

    def RefreshMidiInputs(self):
        if hasattr(self, '_midi_inputs'):
            delattr(self, '_midi_inputs')

    def GetMidiOutputs(self):
        if not hasattr(self, '_midi_outputs'):
            output_device_names, output_device_indexes = pyo.pm_get_output_devices()
            default_output_index = pyo.pm_get_default_output()
            midi_outputs = {}
            for output_index, output_name in zip(output_device_indexes, output_device_names):
                midi_outputs[output_index] = {
                    'name': output_name,
                    'default': bool(output_index == default_output_index),
                }
            setattr(self, '_midi_outputs', midi_outputs)
        return getattr(self, '_midi_outputs')

    def RefreshMidiOutputs(self):
        if hasattr(self, '_midi_outputs'):
            delattr(self, '_midi_outputs')

    def RefreshAudioMidiIO(self):
        self.RefreshAudioInputs()
        self.RefreshAudioOutputs()
        self.RefreshMidiInputs()
        self.RefreshMidiOutputs()

    def OnAudioServerProcessCallback(self):
        pass

    def OnAudioServerMeterCallback(self, *args):
        pass

    def GetAudioServer(self):
        if not hasattr(self, '_pyo_server'):
            self._pyo_server = pyo.Server()
            self._pyo_server.deactivateMidi()
            self._pyo_server.setCallback(self.OnAudioServerProcessCallback)
            self._pyo_server.setMeterCallable(self.OnAudioServerMeterCallback)
            self._pyo_server.boot()
            self._pyo_server.verbosity = 15
        return self._pyo_server

    def GetAudioServerStatus(self):
        if not hasattr(self, '_pyo_server'):
            return 'disabled'
        if self._pyo_server.getIsBooted():
            if self._pyo_server.getIsStarted():
                return 'running'
            else:
                return 'stopped'
        else:
            return 'enabled'

    def RebootAudioServer(self):
        if not hasattr(self, '_reboot_audio_server_call'):
            self._reboot_audio_server_call = wx.CallLater(1, self.OnRebootAudioServer)
        self._reboot_audio_server_call.Start(1000)

    def OnRebootAudioServer(self):
        server = self.GetAudioServer()
        if server.getIsBooted():
            if server.getIsStarted():
                server.stop()
                top_window = self.GetTopWindow()
                if top_window:
                    wx.PostEvent(top_window, AudioServerStoppedEvent(0))
            server.shutdown()
        self.RefreshAudioInputs()
        audio_inputs = self.GetAudioInputs()
        audio_input = self.GetAudioInput()
        if audio_input in audio_inputs:
            server.setInputDevice(audio_input)
        server.boot()
        if audio_input in audio_inputs:
            server.start()
            wx.PostEvent(self.GetTopWindow(), AudioServerStartedEvent(0))

    def ShutdownAudioServer(self):
        if hasattr(self, '_pyo_server'):
            if self._pyo_server and self._pyo_server.getIsBooted():
                if self._pyo_server.getIsStarted():
                    self._pyo_server.stop()
                    top_window = self.GetTopWindow()
                    if top_window:
                        wx.PostEvent(top_window, AudioServerStoppedEvent(0))
                self._pyo_server.shutdown()
            delattr(self, '_pyo_server')

    def OnMidiListenerCallback(self, status, data1, data2, device_id=None):
        pass

    def GetMidiListener(self):
        if not hasattr(self, '_midi_listener'):
            self.RefreshMidiInputs()
            midi_inputs = self.GetMidiInputs()
            midi_input = self.GetMidiInput()
            if midi_input in midi_inputs:
                self._midi_listener = pyo.MidiListener(self.OnMidiListenerCallback, midi_input, reportdevice=True)
                self._midi_listener.start()
            else:
                self._midi_listener = pyo.MidiListener(self.OnMidiListenerCallback, reportdevice=True)
        return self._midi_listener

    def GetMidiListenerStatus(self):
        if not hasattr(self, '_midi_listener'):
            return 'disabled'
        if self._midi_listener.is_alive():
            return 'running'
        else:
            return 'stopped'

    def RebootMidiListener(self):
        if not hasattr(self, '_reboot_midi_listener_call'):
            self._reboot_midi_listener_call = wx.CallLater(1, self.OnRebootMidiListener)
        self._reboot_midi_listener_call.Start(1000)

    def OnRebootMidiListener(self):
        if hasattr(self, '_midi_listener'):
            if self._midi_listener.is_alive():
                self._midi_listener.stop()
                self._midi_listener.join(1.0)
            del self._midi_listener
        self.GetMidiListener()

    def GetMidiDispatcher(self):
        if not hasattr(self, '_midi_dispatcher'):
            self.RefreshMidiOutputs()
            midi_outputs = self.GetMidiOutputs()
            midi_output = self.GetMidiOutput()
            print(midi_outputs, midi_output)
            if midi_output in midi_outputs:
                self._midi_dispatcher = pyo.MidiDispatcher(midi_output)
                self._midi_dispatcher.start()
            else:
                self._midi_dispatcher = pyo.MidiDispatcher()
            print(self._midi_dispatcher.getDeviceInfos())
        return self._midi_dispatcher

    def GetMidiDispatcherStatus(self):
        if not hasattr(self, '_midi_dispatcher'):
            return 'disabled'
        if self._midi_dispatcher.is_alive():
            return 'running'
        else:
            return 'stopped'

    def RebootMidiDispatcher(self):
        if not hasattr(self, '_reboot_midi_dispatcher_call'):
            self._reboot_midi_dispatcher_call = wx.CallLater(1, self.OnRebootMidiDispatcher)
        self._reboot_midi_dispatcher_call.Start(1000)

    def OnRebootMidiDispatcher(self):
        if hasattr(self, '_midi_dispatcher'):
            if self._midi_dispatcher.is_alive():
                if hasattr(self._midi_dispatcher, 'stop'):
                    self._midi_dispatcher.stop()
                else:
                    self._midi_dispatcher._dispatcher.stop()
                self._midi_dispatcher.join(1.0)  # FIXME: Doesn't really stop.
            del self._midi_dispatcher
        self.GetMidiDispatcher()

    def SendMidiEvent(self, status, data1, data2=0, timestamp=0, device=-1):
        if hasattr(self, '_midi_dispatcher') and self._midi_dispatcher.is_alive():
            self._midi_dispatcher.send(status, data1, data2, timestamp, device)

    def SendMidiSysEvent(self, msg, timestamp=0, device=-1):
        if hasattr(self, '_midi_dispatcher') and self._midi_dispatcher.is_alive():
            self._midi_dispatcher.sendx(msg, timestamp, device)

    def OnAudioServerStarted(self, event):
        self.StartAudioInputMeter()
        self.StartAudioStrengthAnalyzer()
        # self.InitBeatGenerator()

    def OnAudioServerStopped(self, event):
        self.StopAudioInputMeter()
        self.StopAudioStrengthAnalyzer()

    def StartAudioInputMeter(self):
        input_meter = wx.FindWindowById(ID_INPUT_METER)
        if not input_meter:
            self.StopAudioInputMeter()
            return

        input_meter_ref = weakref.ref(input_meter)

        def peak_amp_func(*args):
            meter_data = [min(120, max(0, int(-120.0 if arg < 0.000001 else 20.0 * math.log10(arg)) + 90)) for arg in args]
            # meter_data = [min(120, max(0, int(pyo.rescale(arg, 0, 1, 0, 120)))) for arg in args]
            input_meter = input_meter_ref()
            if input_meter:
                input_meter.SetData(meter_data, 0, len(meter_data))

        aic = self.GetAudioInputChannels()
        chans = [n for n in range(8) if (aic & (2 ** n))]
        inp = pyo.Input(chans)
        mix = pyo.Mix(inp, 2)
        self._input_peak_amp = pyo.PeakAmp(mix, peak_amp_func)

    def StopAudioInputMeter(self):
        if hasattr(self, '_input_peak_amp'):
            delattr(self, '_input_peak_amp')

    def OnAudioStrengthVelocity(self, velocity):
        if not hasattr(self, '_strength_gauge'):
            self._strength_gauge = wx.FindWindowById(ID_STRENGTH_GAUGE)
        if self._strength_gauge:
            self._strength_gauge.SetValue(velocity)
            self._strength_gauge.Refresh()
        midi_output = self.GetStrengthMidiOutput()
        if midi_output:
            status = (midi_output & 0xff00) >> 8
            data1 = midi_output & 0xff
            data2 = velocity & 0x7f
            self.SendMidiEvent(status, data1, data2)

    def StartAudioStrengthAnalyzer(self):
        self.UpdateAudioStrengthAnalyzer()

    def UpdateAudioStrengthAnalyzer(self):
        if not hasattr(self, '_strength_analyzer'):
            self._strength_analyzer = StrengthAnalyzer(self.OnAudioStrengthVelocity)
        if self.GetAudioServerStatus() != 'running':
            return

        enabled = self.GetStrengthEnabled()
        if not enabled and self._strength_analyzer.enabled:
            self._strength_analyzer.enabled = enabled

        aic = self.GetAudioInputChannels()
        self._strength_analyzer.input_channels = [n for n in range(16) if aic & (2 ** n)]
        self._strength_analyzer.lpf = self.GetStrengthLPF()
        self._strength_analyzer.attack = self.GetStrengthAttack()
        self._strength_analyzer.release = self.GetStrengthRelease()
        self._strength_analyzer.min_spl = self.GetStrengthMinSPL()
        self._strength_analyzer.min_velocity = self.GetStrengthMinVelocity()
        self._strength_analyzer.max_spl = self.GetStrengthMaxSPL()
        self._strength_analyzer.max_velocity = self.GetStrengthMaxVelocity()

        if enabled and not self._strength_analyzer.enabled:
            self._strength_analyzer.enabled = enabled
        if enabled:
            self._strength_analyzer.play()

    def StopAudioStrengthAnalyzer(self):
        if hasattr(self, '_strength_analyzer'):
            self._strength_analyzer.stop()

    def InitBeatGenerator(self):
        b = pyo.Beat()
        self._bp1 = pyo.Print(b['tap'], 1, message='tap')
        self._bp2 = pyo.Print(b['amp'], 1, message='amp')
        self._bp3 = pyo.Print(b['dur'], 1, message='dur')
        self._bp4 = pyo.Print(b['end'], 1, message='end')
        self._bp5 = pyo.Print(b, 1, message='trg')
        b.play()

    GetLogLevel = lambda s: s.GetSetting('log_level', str, 'normal')

    def SetLogLevel(self, v=None):
        if v is None:
            v = self.GetLogLevel()
        self.SetSetting('log_level', str, v)
        if v == 'debug':
            wx.Log.SetLogLevel(wx.LOG_Debug)
        elif v == 'verbose':
            wx.Log.SetLogLevel(wx.LOG_Info)
        else:
            wx.Log.SetLogLevel(wx.LOG_Status)

    def FormatLogMessage(self, level, msg, ts):
        if isinstance(level, basestring):
            level_name = level
        else:
            level_name = {
                1: 'ERROR',
                2: 'WARNING',
                3: 'INFO',
                4: 'SUCCESS',
                5: 'VERBOSE',
                6: 'DEBUG',
            }.get(level, 'UNKNOWN')
        if isinstance(ts, basestring):
            log_ts = ts
        else:
            log_ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
        msg_lines = msg.splitlines()
        log_fmt = '%s %-7s %s'
        log_indent = len(log_fmt % (log_ts, level_name, '')) * ' '
        log_msg = log_fmt % (log_ts, level_name, msg_lines[0])
        log_lines = textwrap.wrap(log_msg, 120, subsequent_indent=log_indent)
        for msg_line in msg_lines[1:]:
            log_lines.extend(textwrap.wrap(msg_line, 120, initial_indent=log_indent,
                                           subsequent_indent=log_indent))
        log_lines.append('')
        return '\r\n'.join(log_lines)

    def GetResource(self, res_id):
        if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
            return win32api.LoadResource(0, 'beatdown', res_id)
        else:
            res_path = {
                1: './graphics/logo.ico',
            }.get(res_id)
            res_path = os.path.abspath(os.path.join(APP_PATH, res_path))
            return open(res_path, 'rb').read()


def main():
    socket.setdefaulttimeout(15.0)
    logging.basicConfig(level=logging.DEBUG)
    app = App(False)
    app.MainLoop()


if __name__ == '__main__':
    main()
