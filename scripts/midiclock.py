#!/usr/bin/env python

# Python
import functools
import time

# PyO
import pyo


class ClockGenerator(object):

    def __init__(self, bpm=120):
        self.bpm = bpm
        self.next_beat = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        now = time.time()
        #print('A', now, self.next_beat, self.next_beat - now)
        self.next_beat = self.next_beat or now
        if self.next_beat > now:
            time.sleep(self.next_beat - now)
            now = time.time()
        while self.next_beat <= now:
            self.next_beat = self.next_beat + 2.5 / self.bpm
        #print('B', now, self.next_beat, self.next_beat - now)
        return b'\xf8'


class LevelCallback(object):

    def __init__(self, server):
        self.server = server
        self.last_velocity = 0

    def __call__(self, *args):
        print(args)



def meter_callback(server, *args):
    print(args)


def main():
    server = pyo.Server()

    try:
        audio_input_device = None
        audio_input_names, audio_input_indexes = pyo.pa_get_input_devices()
        audio_input_dict = dict(zip(audio_input_indexes, audio_input_names))
        print(audio_input_dict)
        for audio_input_index, audio_input_name in audio_input_dict.items():
            if 'built-in' in audio_input_name.lower():
                if audio_input_device != audio_input_index:
                    server.stop()
                    server.shutdown()
                    server.setInputDevice(audio_input_index)
                    audio_input_device = audio_input_index
                    server.boot()
                    server.start()
                break

        midi_output_device = None
        device_names, device_indexes = pyo.pm_get_output_devices()
        device_dict = dict(zip(device_indexes, device_names))
        print(device_dict)
        for device_index, device_name in device_dict.items():
            # print(device_index, device_name)
            if 'lightkey' in device_name.lower():
                if midi_output_device != device_index:
                    server.stop()
                    server.shutdown()
                    server.setMidiOutputDevice(device_index)
                    midi_output_device = device_index
                    server.boot()
                    server.start()
                break
        #if midi_output_device is None:
        #    return
    
    
        def trig_func(obj):
            print('velocity', obj.stream.getValue())
            velo = int(obj.stream.getValue())
            server.ctlout(28, velo, 1)
            #print(obj, dir(obj))
            #print(obj.stream, dir(obj.stream))

        #mc = functools.partial(meter_callback, server)
        #def mcb(*args, **kwargs):
        #    print(args, kwargs)
        #server.setMeterCallable(mcb)
        lcb = LevelCallback(server)
        inp = pyo.Input([0,1])
        inx = pyo.Mix(inp)
        flr = pyo.Follower(inx)
        scl = pyo.Scale(flr, outmax=31, exp=0.5)
        rnd = pyo.Round(scl)
        #rnds = pyo.Switch(rnd, outs=2)
        #prn = pyo.Print(rnd, 1, message='rnd')
        chg = pyo.Change(rnd)
        #pr2 = pyo.Print(chg, 1, message='chg')
        scl2 = pyo.Scale(rnd, inmax=31, outmin=0, outmax=127)
        rnd2 = pyo.Round(scl2)
        trg = pyo.TrigFunc(chg, trig_func, rnd2)
        
        #pka = pyo.PeakAmp(inp, lcb)
    
        cg = ClockGenerator()
        try:
            server.sysexout(b'\xfa')
            for msg in cg:
                server.sysexout(msg)
        except KeyboardInterrupt:
            server.sysexout(b'\xfc')
            time.sleep(0.1)
            pass
    finally:
        server.stop()
        server.shutdown()


if __name__ == '__main__':
    main()
