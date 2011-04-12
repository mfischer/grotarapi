#!/usr/bin/env python

from gnuradio import uhd
from gnuradio import blks2
from gnuradio import gr
from gnuradio import eng_notation

import time
import struct
import sys
import os
import sys
import shlex
import subprocess
import signal

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

    
def main():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    sys.path.append(os.getcwd())
    from PHY import PhysicalLayer
    
    samples_per_symbol = 4
    samp_rate = 4e6
    tb = gr.top_block()

    modulator = blks2.gmsk_mod(samples_per_symbol=samples_per_symbol)
    demodulator = blks2.gmsk_demod(samples_per_symbol=samples_per_symbol)

    sys.stderr.write('Using bitrate %sbits/s\n' % eng_notation.num_to_str(samp_rate / samples_per_symbol / modulator.bits_per_symbol()))
    sys.stderr.flush()
    phy = PhysicalLayer.PhysicalLayer(modulator, demodulator, hint = 'addr=192.168.10.2', access_code = 'master')
    tb.connect(phy)
    
    phy.tune(1.8e9)
    phy.set_gain(45)
    phy.set_samp_rate(samp_rate)

    args = shlex.split('cvlc --sout "#transcode{acodec=vorbis, ab=48}:std{access=file, mux=ogg, dst=-}" seek.mp3')
    child = subprocess.Popen(args, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr=None)
    #print 'Started vlc with pid', child.pid

    def read_data_from_child():
        print "[DEBUG] reading from child's pipe"
        phy.send_pkt(child.stdout.read(512))
        return True

    tb.start()
    gobject.threads_init()
    gobject.idle_add(read_data_from_child)
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
