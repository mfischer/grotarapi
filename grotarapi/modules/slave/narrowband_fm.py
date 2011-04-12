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
# Generated: Tue Mar  1 14:25:52 2011
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import forms
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Top Block")

		##################################################
		# Variables
		##################################################
		self.variable_slider_0 = variable_slider_0 = 0
		self.samp_rate = samp_rate = 500e3

		##################################################
		# Controls
		##################################################
		_variable_slider_0_sizer = wx.BoxSizer(wx.VERTICAL)
		self._variable_slider_0_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_variable_slider_0_sizer,
			value=self.variable_slider_0,
			callback=self.set_variable_slider_0,
			label="Volume",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._variable_slider_0_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_variable_slider_0_sizer,
			value=self.variable_slider_0,
			callback=self.set_variable_slider_0,
			minimum=0,
			maximum=100,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_variable_slider_0_sizer)

		##################################################
		# Blocks
		##################################################
		self.audio_sink_0 = audio.sink(48000, "", True)
		self.blks2_nbfm_rx_0 = blks2.nbfm_rx(
			audio_rate=25000,
			quad_rate=100000,
			tau=75e-6,
			max_dev=15e3,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=1,
			decimation=5,
			taps=None,
			fractional_bw=None,
		)
		self.blks2_rational_resampler_xxx_1 = blks2.rational_resampler_fff(
			interpolation=48,
			decimation=25,
			taps=None,
			fractional_bw=None,
		)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((variable_slider_0, ))
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vcc((100e3, ))
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			10, samp_rate, 5e3, 10e3, firdes.WIN_HAMMING, 6.76))
		self.uhd_single_usrp_source_0 = uhd.single_usrp_source(
			device_addr="addr=192.168.10.3",
			io_type=uhd.io_type.COMPLEX_FLOAT32,
			num_channels=1,
		)
		self.uhd_single_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_single_usrp_source_0.set_center_freq(462.5625e6, 0)
		self.uhd_single_usrp_source_0.set_gain(45, 0)
		self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
			self.GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=50,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Waterfall Plot",
		)
		self.Add(self.wxgui_waterfallsink2_0.win)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_nbfm_rx_0, 0), (self.blks2_rational_resampler_xxx_1, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.blks2_nbfm_rx_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_1, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.uhd_single_usrp_source_0, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.low_pass_filter_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.wxgui_waterfallsink2_0, 0))

	def set_variable_slider_0(self, variable_slider_0):
		self.variable_slider_0 = variable_slider_0
		self.gr_multiply_const_vxx_0.set_k((self.variable_slider_0, ))
		self._variable_slider_0_slider.set_value(self.variable_slider_0)
		self._variable_slider_0_text_box.set_value(self.variable_slider_0)

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
		self.uhd_single_usrp_source_0.set_samp_rate(self.samp_rate)
		self.low_pass_filter_0.set_taps(firdes.low_pass(10, self.samp_rate, 5e3, 10e3, firdes.WIN_HAMMING, 6.76))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

