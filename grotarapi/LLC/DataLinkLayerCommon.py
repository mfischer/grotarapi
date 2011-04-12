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

import struct
import time
import sys

class DataLinkLayer(object):
    def __init__(self, mac, type):
        print 'Created %s Data Link Layer' % type
        self.mac = mac
        self.mac.set_rx_callback(self.rx_callback)
        self.callback = None

    def set_rx_callback(self, callback):
        self.callback = callback
    
    def rx_callback(self, data):
        pass
        
