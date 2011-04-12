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

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gtk

def print_stuff(data):
    toController(data)

    
def main():
    sys.path.append(os.getcwd())
    from MAC import MacLayer
    from PHY import PhysicalLayer
    import LLC.SlidingWindow
    
    samples_per_symbol = 2
    samp_rate = 4e6

    tb = gr.top_block()

    modulator = blks2.gmsk_mod(samples_per_symbol=samples_per_symbol)
    demodulator = blks2.gmsk_demod(samples_per_symbol=samples_per_symbol)

    sys.stderr.write('Using bitrate %sbits/s\n' % eng_notation.num_to_str(samp_rate / samples_per_symbol / modulator.bits_per_symbol()))
    sys.stderr.flush()
    phy = PhysicalLayer.PhysicalLayer(modulator, demodulator, hint = 'addr=192.168.10.3', access_code = 'slave')
    #phy = PhysicalLayer.PhysicalLayer(modulator, demodulator, hint = 'type=usrp1', access_code = 'slave')
    mac = MacLayer.SimpleMacLayer(phy, addr = True)
    llc = LLC.SlidingWindowDataLinkLayer(mac, wr = 1500, wt = 4000)

    def cleanup():
        tb.stop()
        sys.exit(0)
    tb.connect(phy)
    
    phy.tune(1.8e9)
    phy.set_gain(45)
    phy.set_samp_rate(samp_rate)

    #dbus stuff
    DBusGMainLoop(set_as_default = True)
    bus = dbus.SessionBus()
    service = bus.get_object('org.gnuradio.grotarapi',
                             '/org/gnuradio/grotarapi/controller/slave')
    iface = dbus.Interface(service, dbus_interface = 'org.gnuradio.grotarapi.guts')
    def send_data(data):
        sys.stderr.write('[Slave Child] trying to send data %s\n' % data)
        sys.stderr.flush()
        llc.send_pkt(str(data))

    iface.connect_to_signal("send_data", send_data)
    llc.set_rx_callback(iface.rx_callback_binary)
    tb.start()
    gobject.threads_init()
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
