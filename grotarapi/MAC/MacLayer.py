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

import time
import struct

from gnuradio import uhd
from gnuradio import blks2
from gnuradio import gr

import Packets

class SimpleMacLayer(object):
    """
    A real simple MAC layer, all it does at the moment is to decide whether the
    packet is for us or not. I.e. whether we sent the packet before.
    """
    def __init__(self, phy, addr = False):
        #print 'Created MAC layer!'
        self.phy = phy
        self.phy.set_rx_callback(self.rx_callback)
        self.addr = addr

    def rx_callback(self, ok, data):
        if ok:
            pkt = Packets.MacPacket(None, None, binary = data)
            #print "[MAC] Type of the payload of packet" ,type(pkt.payload), "\n"
            if(self.addr == pkt.addr):
                #print 'MAC Layer received packet with payload %s, length is %d' % (pkt.payload, len(data))
                self.rx_callback(ok, pkt.payload)
   
    def send_pkt(self, data):
        pkt = Packets.MacPacket(data, not self.addr)
        self.phy.send_pkt(str(pkt))
    
    def set_rx_callback(self, callback):
        self.rx_callback = callback

    def get_mtu(self):
        return 1500
