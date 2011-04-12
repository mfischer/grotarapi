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

class MacPacket(object):
    def __init__(self, payload = '', addr = None, binary = None, payload_max = 2000):
        self.payload_max = 2000

        self.header_fmt = '!I?'
        self.header_len = struct.calcsize(self.header_fmt)

        if payload is None: #FIXME Dirty hack
            payload = ''

        if payload is '' and addr is None and binary is None:
            print "Can't build packet like this!\n"

        # handle the case for a binary packet 
        elif binary is not None:
            header = binary[0:self.header_len]
            remainder = binary[self.header_len:]
            self.payload_len, self.addr = struct.unpack(self.header_fmt, header)
            self.payload = struct.unpack('!%ds' % self.payload_len, remainder)[0] #TODO Beautify

        # we have to build a packet with the given values
        else:
            if addr is None:
                addr = 'True'
                print 'Building a MAC packet without adress! This should not happen!\n'
            
            if len(payload) > payload_max:
                self.payload = payload[0:payload_max]
                print 'Trying to build a packet with too much payload! Trunkating payload! This should not happen\n'
            else:
                self.payload = payload

            self.payload_len = len(self.payload)
            self.addr = addr
            self.binary = struct.pack(self.header_fmt+'%ds' % self.payload_len, self.payload_len, self.addr, self.payload)

        #print "[MAC Packet] Type of self.payload", type(self.payload), "\n"

    def __str__(self):
         return self.binary

