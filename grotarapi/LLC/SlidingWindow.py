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
import Packets
import gobject

class llc_transmitter(object):
    """ 
    This class contains the transmitter part of the sliding window implementation
    @param mac: The MAC Layer you want to use
    @type mac: Custom class see code for examples
    @param wt: The transmit window, i.e: How many packets will be send
               after the last ACK received.
    @type wt: number, bigger than the corresponding wr in the receiver
    """

    def __init__(self, mac, wt = 128, timeout = 100):
        self.mac = mac
        self.wt = wt
        self.na = 0
        self.nt = 0
        self.buf = []
        self.timeout = timeout
        gobject.idle_add(self.transmit_missing)

        #print '[LLC] Initialized LLC with wt = %d' % self.wt

    def send_pkt(self, payload):
        if self.nt < self.nt + self.wt:
            pkt = Packets.LLCPacket(seq_no = self.nt, cmd = 'D', payload = payload)
            self.buf.append(pkt)
            self.nt += 1
            self.mac.send_pkt(pkt.binary)
        else:
            print '[LLC] We reached the upper bound of the window!'

    def transmit_missing(self):
        if not (self.na == self.nt):
            #print '[LLC] Waiting for ACK of seq_no self.nt = %d!' %self.nt
            for pkt in self.buf:
                self.mac.send_pkt(pkt.binary)
        return True

    def ack_received(self, seq_no):
        if self.na < seq_no:
            ackd_packets = int(seq_no - self.na)
            self.na = seq_no
            self.buf = self.buf[ackd_packets:]
            #print '[LLC] We received an ack for seq# %d' % seq_no
        elif self.na == seq_no:
            pass
        else:
            pass
            #self.reset()
            #pkt = Packets.LLCPacket(seq_no = seq_no, cmd = 'R', payload='RESET')
            #self.reset()
            #self.mac.send_pkt(pkt.binary)

class llc_receiver(object):
    """ 
    This class contains the receiver part of the sliding window implementation
    @param mac: The MAC Layer you want to use
    @type mac: Custom class see code for examples
    @param wr: The Receive window, i.e: How many packets will be buffered 
               after the last one that was ok
    @type wr: number, smaller than the corresponding wt in the transmitter
    """
    def __init__(self, mac, wr = 100):
        self.mac = mac
        self.wr = wr
        self.buf = {}
        self.nr = 0
        #print '[LLC] Initialized LLC with wr = %d' % self.wr

    def _send_ack(self, seq_no):
        #print '[LLC] sending ACK for seq_no: %u' % seq_no
        pkt = Packets.LLCPacket(seq_no = seq_no, cmd = 'A', payload='ACK')
        self.mac.send_pkt(pkt.binary)
        return False

    def rx_callback(self, payload):
        pass

    def receive_packet(self, pkt):
        #print '[LLC] Received packet with seq.no %u' % pkt.seq_no
        if pkt.seq_no == self.nr:
            self._send_ack(self.nr)
            self.nr += 1
            #TODO figure out why high timout is needed, time for ACK to arrive?
            gobject.timeout_add(20, self.rx_callback, pkt.payload) 
            while(self.buf.has_key(self.nr)):
                self._send_ack(self.nr) 
                gobject.timeout_add(90, self.rx_callback, pkt.payload)
                self.nr += 1

        elif (pkt.seq_no > self.nr) and (pkt.seq_no < (self.nr + self.wr)):
            print '[LLC] We received something inside wr, bigger than nr'
            self.buf[pkt.seq_no] = pkt
            self._send_ack(self.nr)

        # Those are the retransmission of already received ones so we tell the sender the last one we received
        else:
            self._send_ack(self.nr)
            #print '[LLC] Seqno: %d, self.nr = %d, window (%d,%d]' %(pkt.seq_no, self.nr, self.nr, self.nr+self.wr)

class SlidingWindowDataLinkLayer(object):
    """
    This class is a sliding window flow control implementation. See the corresponding
    Wikipedia article on how this works:

    http://en.wikipedia.org/wiki/Sliding_window_protocol

    @type mac: Custom class, see code for examples
    @param wt: See documentation of llc_transmitter
    @type wt: number, bigger than the corresponding wr in the receiver
    @param wr: See documentation of llc_receiver
    @type wr: number, smaller than the corresponding wt in the transmitter
    """
    def __init__ (self, mac, wt = 128, wr = 100, timeout=0.01):
        if wt < wr: 
            print "This doesn't make sense as packets with seq_no > wr will be dropped anyway"
        self.llc_transmitter = llc_transmitter(mac, wt, timeout)
        self.llc_receiver = llc_receiver(mac, wr)

        self.mac = mac
        self.mac.set_rx_callback(self.rx_callback)

    def rx_callback(self, ok, payload):
        #print 'LLC received packet of length %d' % len(payload)
        pkt = Packets.LLCPacket(binary = payload)
        if ok:
            if pkt.is_ack():
                #print "[LLC] Received an ACK for %d\n" % pkt.seq_no
                self.llc_transmitter.ack_received(pkt.seq_no)
            else:
                ##print "[LLC] Received a normal packet\n"
                self.llc_receiver.receive_packet(pkt)
                #print "[LLC] payload -%s-\n" % pkt.payload

    def send_pkt(self, payload):
        self.llc_transmitter.send_pkt(payload)

    def set_rx_callback(self, handle):
        self.llc_receiver.rx_callback = handle
        #print "[LLC] Registered Behaviour's callback"
