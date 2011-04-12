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
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Tue Mar  1 14:36:23 2011
##################################################

from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Top Block")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 500e3

		##################################################
		# Blocks
		##################################################
		self.blks2_nbfm_tx_0 = blks2.nbfm_tx(
			audio_rate=25000,
			quad_rate=100000,
			tau=75e-6,
			max_dev=5e3,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=5,
			decimation=1,
			taps=None,
			fractional_bw=None,
		)
		self.gr_multiply_xx_0 = gr.multiply_vcc(1)
		self.gr_sig_source_x_0 = gr.sig_source_c(samp_rate, gr.GR_COS_WAVE, 6.9e3, 1, 0)
		self.gr_wavfile_source_0 = gr.wavfile_source("classical.wav", True)
		self.uhd_single_usrp_sink_0 = uhd.single_usrp_sink(
			device_addr="addr=192.168.10.2",
			io_type=uhd.io_type.COMPLEX_FLOAT32,
			num_channels=1,
		)
		self.uhd_single_usrp_sink_0.set_samp_rate(samp_rate)
		self.uhd_single_usrp_sink_0.set_center_freq(462.5625e6, 0)
		self.uhd_single_usrp_sink_0.set_gain(30, 0)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_wavfile_source_0, 0), (self.blks2_nbfm_tx_0, 0))
		self.connect((self.blks2_nbfm_tx_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_multiply_xx_0, 0))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_multiply_xx_0, 1))
		self.connect((self.gr_multiply_xx_0, 0), (self.uhd_single_usrp_sink_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.uhd_single_usrp_sink_0.set_samp_rate(self.samp_rate)
		self.gr_sig_source_x_0.set_sampling_freq(self.samp_rate)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

