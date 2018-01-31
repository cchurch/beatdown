# Python
import math
import threading

# PyO
import pyo


class MidiListener(pyo.MidiListener):

    def __init__(self, *args, **kwargs):
        super(MidiListener, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def run(self):
        self._listener.play()
        while not self._stop_event.wait(0.1):
            pass
        self._listener.stop()
        self._stop_event.clear()

    def stop(self):
        self._stop_event.set()


class MidiDispatcher(pyo.MidiDispatcher):

    def __init__(self, *args, **kwargs):
        super(MidiDispatcher, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def run(self):
        self._dispatcher.play()
        while not self._stop_event.wait(0.1):
            pass
        self._dispatcher.stop()
        self._stop_event.clear()

    def stop(self):
        self._stop_event.set()


class BeatGenerator(object):

    def __init__(self, callback=None):
        self._callback = callback
        self._enabled = False
        self._bpm = 120
        self._sig = None
        self._met = None
        self._trg = None

    def _trig_callback(self):
        if self._callback:
            self._callback(b'\xf8')

    def play(self):
        if not self._sig:
            self._sig = pyo.Sig(value=self._bpm)
        if not self._met:
            tpb = 2.5 / (pyo.Clip(pyo.Round(self._sig), 30, 360))
            self._met = pyo.Metro(time=tpb)
            self._met.play()
            if self._callback:
                self._callback(b'\xfa')
        if not self._met.isPlaying():
            self._met.play()
            if self._callback:
                self._callback(b'\xfb')
        if not self._trg:
            self._trg = pyo.TrigFunc(self._met, self._trig_callback)

    def pause(self):
        if self._met and self._met.isPlaying():
            self._met.stop()
            if self._callback:
                self._callback(b'\xfc')

    def isPaused(self):
        return bool(not self._met or not self._met.isPlaying())

    def stop(self):
        self.pause()
        self._sig = None
        self._met = None
        self._trg = None

    def getEnabled(self):
        return self._enabled

    def setEnabled(self, value):
        value = bool(value)
        if self.enabled != value:
            self._enabled = value
        if value:
            self.play()
        else:
            self.stop()

    def getBPM(self):
        return self._bpm

    def setBPM(self, value):
        value = min(360, max(30, int(value)))
        if self._bpm != value:
            self._bpm = value
            if self._sig:
                self._sig.setValue(self._bpm)

    enabled = property(getEnabled, setEnabled)
    bpm = property(getBPM, setBPM)


class StrengthAnalyzer(object):

    def __init__(self, callback=None):
        self._callback = callback
        self._enabled = False
        self._input_channels = [0]
        self._lpf = 120
        self._attack = 0.1
        self._release = 0.1
        self._min_spl = -120
        self._min_velocity = 0
        self._max_spl = 0
        self._max_velocity = 127
        self._midi_output = 0
        self._but_lp = None
        self._follower = None
        self._peak_amp = None

    def _peak_amp_callback(self, *args):
        amp = args[0] if args else 0.0
        spl = -120.0 if amp < 0.000001 else 20.0 * math.log10(amp)
        if spl <= self._min_spl:
            velocity = self._min_velocity
        elif spl >= self._max_spl:
            velocity = self._max_velocity
        else:
            velocity = int(pyo.rescale(spl, self._min_spl, self._max_spl, self._min_velocity, self._max_velocity))
        if self._callback:
            self._callback(velocity)

    def play(self):
        if not self._but_lp:
            inp = pyo.Input(self._input_channels)
            mix = pyo.Mix(inp)
            self._but_lp = pyo.ButLP(mix, self._lpf)
        if not self._follower:
            self._follower = pyo.Follower2(self._but_lp, risetime=self._attack, falltime=self._release)
        if not self._peak_amp:
            self._peak_amp = pyo.PeakAmp(self._follower, self._peak_amp_callback)

    def stop(self):
        self._peak_amp = None
        self._follower = None
        self._but_lp = None

    def getEnabled(self):
        return self._enabled

    def setEnabled(self, value):
        value = bool(value)
        if self.enabled != value:
            self._enabled = value
        if value:
            self.play()
        else:
            self.stop()

    def getInputChannels(self):
        return self._input_channels

    def setInputChannels(self, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        if self._input_channels != value:
            self._input_channels = value
            if self._but_lp:
                inp = pyo.Input(self._input_channels)
                mix = pyo.Mix(inp)
                self._but_lp.setInput(mix)

    def getLPF(self):
        return self._lpf

    def setLPF(self, value):
        value = min(20000, max(20, int(value)))
        if self._lpf != value:
            self._lpf = value
            if self._but_lp:
                self._but_lp.setFreq(self._lpf)

    def getAttack(self):
        return self._attack

    def setAttack(self, value):
        value = min(10.0, max(0.0, float(value)))
        if self._attack != value:
            self._attack = value
            if self._follower:
                self._follower.setRisetime(self._attack)

    def getRelease(self):
        return self._release

    def setRelease(self, value):
        value = min(10.0, max(0.0, float(value)))
        if self._release != value:
            self._release = value
            if self._follower:
                self._follower.setFalltime(self._release)

    def getMinSPL(self):
        return self._min_spl

    def setMinSPL(self, value):
        self._min_spl = max(-120, min(0, value))

    def getMinVelocity(self):
        return self._min_velocity

    def setMinVelocity(self, value):
        self._min_velocity = int(max(0, min(127, value)))

    def getMaxSPL(self):
        return self._max_spl

    def setMaxSPL(self, value):
        self._max_spl = max(-120, min(0, value))

    def getMaxVelocity(self):
        return self._max_velocity

    def setMaxVelocity(self, value):
        self._max_velocity = int(max(0, min(127, value)))

    enabled = property(getEnabled, setEnabled)
    input_channels = property(getInputChannels, setInputChannels)
    lpf = property(getLPF, setLPF)
    attack = property(getAttack, setAttack)
    release = property(getRelease, setRelease)
    min_spl = property(getMinSPL, setMinSPL)
    min_velocity = property(getMinVelocity, setMinVelocity)
    max_spl = property(getMaxSPL, setMaxSPL)
    max_velocity = property(getMaxVelocity, setMaxVelocity)
