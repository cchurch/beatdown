#!/usr/bin/env python
'''
Enable InControl mode on Launchpad Mini (send a C1 note).
'''

# Python
import time

# PyO
import pyo

server = pyo.Server()

try:
    server.boot()
    midi_output_device = None
    while True:
        try:
            device_names, device_indexes = pyo.pm_get_output_devices()
            device_dict = dict(zip(device_indexes, device_names))
            for device_index, device_name in device_dict.items():
                print(device_index, device_name)
                if 'incontrol' in device_name.lower():
                    if midi_output_device != device_index:
                        server.shutdown()
                        server.setMidiOutputDevice(device_index)
                        midi_output_device = device_index
                        server.boot()
                    break
            server.noteout(12, 127)
            time.sleep(10)
        except KeyboardInterrupt:
            break
finally:
    server.shutdown()
