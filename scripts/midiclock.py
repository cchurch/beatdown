#!/usr/bin/env python
'''
Test code to send MIDI beat clock to Lightkey.
'''

# Python
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


def main():
    server = pyo.Server()

    try:
        midi_output_device = None
        device_names, device_indexes = pyo.pm_get_output_devices()
        device_dict = dict(zip(device_indexes, device_names))
        print(device_dict)
        for device_index, device_name in device_dict.items():
            print(device_index, device_name)
            if 'lightkey' in device_name.lower():
                if midi_output_device != device_index:
                    server.stop()
                    server.shutdown()
                    server.setMidiOutputDevice(device_index)
                    midi_output_device = device_index
                    server.boot()
                    server.start()
                break
        if midi_output_device is None:
            return

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
