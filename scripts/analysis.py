#!/usr/bin/env python

# Python
import functools
import time

# PyO
import pyo


def test_metronome(server):
    def trig_func():
        print(server.getCurrentTime(), 'trig')

    inp = pyo.Input([0,1])
    inx = pyo.Mix(inp)
    #atd = pyo.AttackDetector(inx)
    #prn = pyo.Print(atd, 1, message='attack')
    #avg = pyo.Average(inx)
    #prn = pyo.Print(avg, 1, message='avg')
    #sig = pyo.Sig(0.5)
    bpm = pyo.Sig(value=120)
    #bpm_round = pyo.Round(bpm)
    #bpm2 = pyo.Clip(bpm2, 30, 360)
    tpb = 2.5 / (pyo.Clip(pyo.Round(bpm), 30, 360))
    met = pyo.Metro(time=tpb)
    met.play()
    print(server.getBufferSize())
    trg = pyo.TrigFunc(met, trig_func)

    #ti = pyo.Timer(met, met)
    #prn = pyo.Print(met, 1, message='met')
    #bpm = pyo.Round(60 / ti)
    #bpm2 = pyo.Clip(bpm, 30, 360)
    #pr2 = pyo.Print(pyo.Clip(pyo.Round(60 / ti), 30, 360), 0, message='bpm')
    
    def update_met():
        print('update met')
        #met.setTime(0.4)
        bpm.setValue(150)
        #met.stop()
        #met.play()
    ca = pyo.CallAfter(update_met, 10)

    return bpm, trg, ca

def test_table(server):
    def process(): 
        data = table.getTable()
        # "data" is a list of floats of length "buffer size". 

    # Register the "process" function to be called at the beginning 
    # of every processing loop. 
    server.setCallback(process) 

    # Create a table of length `buffer size`. 
    table = pyo.DataTable(size=server.getBufferSize()) 

    inp = pyo.Input([0,1])
    mix = pyo.Mix(inp)

    # Fill the table with the audio signal every processing loop. 
    tfl = TableFill(mix, table)

    return tfl


def test_beat2(server):
    
    inp = pyo.Input([0, 1])
    mix = pyo.Mix(inp)
    
    ad = pyo.AttackDetector(mix, 0.005, 10, 3, -30, 0.1)
    ad.ctrl()
    tmr = pyo.Timer(ad, ad)
    prn = pyo.Print(tmr, 1, message='tmr')
    return ad, prn
    
    #mix = pyo.Noise()
    flr1 = pyo.Follower2(mix, 0.005, 0.005)
    spl1 = pyo.AToDB(flr1)
    flr2 = pyo.Follower2(mix, 0.1, 0.1)
    spl2 = pyo.AToDB(flr2)
    diff = spl2 - spl1
    thr = pyo.Thresh(diff, 6)
    nxt = pyo.TrackHold(diff, thr, 1)
    tmr = pyo.Timer(thr, thr)
    prn = pyo.Print(tmr, 1, message='thr')

    return prn,nxt


def test_beat3(server):
    
    inp = pyo.Input([0, 1])
    mix = pyo.Mix(inp)
    
    gt = pyo.Gate(mix, -30, outputAmp=True)
    prn = pyo.Print(gt, 1, message='gt')
    return prn
    
    ad = pyo.AttackDetector(mix, 0.005, 10, 3, -30, 0.1)
    ad.ctrl()
    tmr = pyo.Timer(ad, ad)
    prn = pyo.Print(tmr, 1, message='tmr')
    return ad, prn
    
    #mix = pyo.Noise()
    flr1 = pyo.Follower2(mix, 0.005, 0.005)
    spl1 = pyo.AToDB(flr1)
    flr2 = pyo.Follower2(mix, 0.1, 0.1)
    spl2 = pyo.AToDB(flr2)
    diff = spl2 - spl1
    thr = pyo.Thresh(diff, 6)
    nxt = pyo.TrackHold(diff, thr, 1)
    tmr = pyo.Timer(thr, thr)
    prn = pyo.Print(tmr, 1, message='thr')

    return prn,nxt


def test_beat(server):
    # Based on http://damian.pecke.tt/beat-detection-on-the-arduino

    server.server_ms = 0
    last_ms = 0
    server.last_bpm = 0
    server.bpms = []
    server.last_avg = 0

    def trig_func():
        #ct = server.getCurrentTime()
        delta = server_ms - last_ms
        last_ms = server_ms
        
        #delta = ct - last_ct
        #bpm = 
        print(delta, 'trig')

    def time_callback(hours, minutes, seconds, milliseconds):
        #print(hours, minutes, seconds, milliseconds)
        server.server_ms = hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds

    def process_callback():
        if ad.minthresh != thr.get():
            ad.minthresh = thr.get()
        #if server.last_avg != avg.get():
        #    print('avg', avg.get())
        #    server.last_avg = avg.get()
        return 
        #bpm = 120 / (tmr.get() or 0.001)
        #while bpm > 360:
        #    bpm /= 2
        #while bpm < 40:
        #    bpm *= 2
        #print('bpm?', bpm)
        data = table.getTable()
        if len(data):
            #data = [d for d in data if d]
            #print(len(data), sum(data), server.server_ms)
            bpm = len(data) * 60 / (sum(data) or 0.001)
            while bpm > 360:
                bpm /= 2
            while bpm < 40:
                bpm *= 2
            #server.bpms.append()
            bpm = int(bpm)
            if bpm != server.last_bpm:
                server.last_bpm = bpm
                print('bpm?', bpm)
        
        table.reset()
        #tfl.play()
            #print(ad.minthresh)

    server.setTimeCallable(time_callback)
    server.setCallback(process_callback)

    table = pyo.DataTable(size=32) 

    inp = pyo.Input([0, 1])
    mix = pyo.Mix(inp)
    
    #mix = pyo.Noise()
    
    #blp = pyo.ButLP(mix, 200)
    #bhp = pyo.ButHP(blp, 20)
    flr = pyo.Follower2(mix, 0.5, 0.5)
    fla = pyo.Average(flr, server.getBufferSize())
    #flr.ctrl()
    spl = pyo.AToDB(flr)
    thr = spl - 6
    ad = pyo.AttackDetector(mix, 0.005, 1000, 12, -30, 0.05)
    #ad.ctrl()
    #prn = pyo.Print(ad, 1, message='ad')
    prn = None
    tmr = pyo.Timer(ad, ad)
    #avg = pyo.Average(tmr, server.getBufferSize())
    #bpm = 60 / pyo.Min(tmr, 0.001)
    #trg = pyo.TrigFunc(ad, trig_func)
    prn2 = pyo.Print(tmr, 1, message='tmr')
    #tfl = pyo.TableFill(tmr, table)
    return ad, prn, thr, prn2#, tfl
    
    
    # 20 - 200hz Bandpass Filter
    #q = pyo.Sig(.1) # No idea what Q should be...
    bpf = pyo.ButBP(mix, 63.245, 9.1)
    ab = pyo.Abs(bpf)
    lpf = pyo.ButLP(ab, 10)
    bp2 = pyo.ButBP(lpf, 2.57, 9)
    
    #server.setCallback()
    sp = pyo.Spectrum(bp2)
    
    return bpf, sp, lpf, bp2

def main():
    server = pyo.Server().boot()

    try:
        audio_input_device = None
        audio_input_names, audio_input_indexes = pyo.pa_get_input_devices()
        audio_input_dict = dict(zip(audio_input_indexes, audio_input_names))
        print(audio_input_dict)
        for audio_input_index, audio_input_name in audio_input_dict.items():
            if 'built-in' in audio_input_name.lower():
                if audio_input_device != audio_input_index:
                    if server.getIsBooted():
                        if server.getIsStarted():
                            server.stop()
                        server.shutdown()
                    server.setInputDevice(audio_input_index)
                    audio_input_device = audio_input_index
                    server.boot()
                    server.start()
                break

        #def process_callback():
        #    pass

        #server.setCallback(process_callback)

        #res = test_metronome(server)
        
        res = test_beat3(server)
        


        #bpm.ctrl()#[pyo.SLMap(30, 360, 'lin', 120, 'int', dataOnly=True)])
        server.gui(locals(), timer=False)
        #try:
        #    while True:
        #        time.sleep(1)
        #except KeyboardInterrupt:
        #    pass
    finally:
        if server.getIsBooted():
            if server.getIsStarted():
                server.stop()
            server.shutdown()


if __name__ == '__main__':
    main()
