# This file is part of GROTARAPI
# GROTARAPI is a free software demonstrator for prototyping
# cognitive radio terminals with GNU Radio and Python.
# Copyright (C) 2011 Communications Engineering Lab, KIT

# GROTARAPI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# GROTARAPI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gtk

def print_stuff(data):
    toController(data)

    
def main():
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

    args = shlex.split('cvlc --sout "#transcode{vcodec=theora, vb=128}:std{access=file, mux=ogg, dst=-}" v4l2:///dev/video0')
    child = subprocess.Popen(args, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr=None)
    print 'Started vlc with pid', child.pid

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
