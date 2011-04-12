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

_SEQ_NO_ERROR = -1

class LLCPacket(object):
    def __init__(self, seq_no = _SEQ_NO_ERROR, cmd = None, payload = '', binary = None):
        self.seq_no = seq_no
        self.cmd = cmd
        self.binary = binary
        self.payload = payload
        self.payload_len = len(payload)

        self.header_fmt = '!IcI'
        self.header_len = struct.calcsize(self.header_fmt)

        if seq_no is _SEQ_NO_ERROR and cmd is None and binary is None:
            print "Can't build packet like this!\n"
        
        # we received a packet in binary form
        elif binary is not None:
            # first we unpack the header
            header = binary[0:self.header_len]
            remainder = binary[self.header_len:]

            self.seq_no, self.cmd , self.payload_len = struct.unpack(self.header_fmt, header)

            # if it's not a ACK/NAK we want the data
            if self.cmd != 'N' or self.cmd != 'A':
                self.payload = struct.unpack('!%ds' %self.payload_len, remainder)[0]

            # it's a NAK/ ACK, so we need the missing/ acked packet
            else:
                #self.payload = struct.unpack('!d',binary[self.header_len:])
                pass

        # we have to build a packet
        else:
            if len(payload) is not 0:
                self.binary = struct.pack(self.header_fmt+'%ds' % len(payload) , seq_no, cmd, len(payload), payload)
            else:
                pass

    def is_ack(self):
        return (self.cmd == 'A')

    def is_nak(self):
        return (self.cmd == 'N')

    def is_reset(self):
        return (self.cmd == 'R')
