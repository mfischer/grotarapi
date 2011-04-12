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

#!/usr/bin/env python2

from gnuradio import uhd
from gnuradio import blks2
from gnuradio import gr

class PhysicalLayer(gr.hier_block2):
    """
    A simple physical layer providing the needed methods to upper layers
    @param hint: decribes the type of USRP to search for e.g. 'type=usrp1'
    @param rx_callback: method that will be called when a packet arrives
    @param modulator: modulator to use
    @param demodulator: demod to use  
    """
    def __init__(self, modulator, demodulator, access_code = None, hint = 'addr=192.168.10.2'):
        gr.hier_block2.__init__(self, "Physical Layer", 
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(0, 0, 0))
        if access_code is 'master':
           self.rx_offset = 8e6
           access_code = None
        elif access_code is 'slave':
           self.rx_offset = -8e6
           access_code = None
        else:
           self.rx_offset = 0

        # create TX/RX
        self.u_tx = uhd.single_usrp_sink(hint, io_type=uhd.io_type_t.COMPLEX_FLOAT32, num_channels=1)
        self.u_rx = uhd.single_usrp_source(hint, io_type=uhd.io_type_t.COMPLEX_FLOAT32, num_channels=1)

        self.access_code = access_code

        # create packetmods
        self.pkt_mod = blks2.mod_pkts(modulator, pad_for_usrp = True, access_code = self.access_code)
        self.pkt_demod = blks2.demod_pkts(demodulator, callback = self.rx_callback, access_code = self.access_code)

        self.connect(self.u_rx, self.pkt_demod)
        self.connect(self.pkt_mod, self.u_tx)
    
    def _callback(self, ok, data):
        pass

    def tune(self, target_freq):
        self.u_rx.set_center_freq(target_freq + self.rx_offset, 0)
        self.u_tx.set_center_freq(target_freq - self.rx_offset, 0)

    def set_gain(self, gain):
#        print 'Physical Layer received a set_gain() request!'
        self.u_rx.set_gain(gain, 0)
        self.u_tx.set_gain(gain, 0)

    def set_samp_rate(self, samp_rate):
#        print 'Physical Layer received a set_samp_rate() request!'
        self.u_rx.set_samp_rate(samp_rate)
        self.u_tx.set_samp_rate(samp_rate)
    
    def set_rx_callback(self, callback):
        self._callback = callback
        #print 'Registered callback for MAC!'

    def rx_callback(self, ok, data):
        self._callback(ok, data)

    def send_pkt(self, data):
        self.pkt_mod.send_pkt(data)

