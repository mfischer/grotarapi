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

import GrotarAPI
import ModuleManager

import subprocess
import shlex
import sys
import gnupg
import os
import signal

import dbus
import dbus.service
import gobject
from dbus.mainloop.glib import DBusGMainLoop

class Controller(dbus.service.Object):
    def __init__(self,
                 master = False,
                 mod_path = 'modules',
                 verbose = False):
        DBusGMainLoop(set_as_default = True)
        bus_name = dbus.service.BusName('org.gnuradio.grotarapi',
                                         bus=dbus.SessionBus())
        self.verbose = verbose
        self.master = master
        f = lambda: master == True and 'master' or 'slave'
        self.gpg = gnupg.GPG(gnupghome=mod_path + '/' + f() + '/gnupghome')
        if self.verbose:
            for key in self.gpg.list_keys():
                print '[INFO] CONTROLLER public key with fingerprint', key['fingerprint']

        if master:
            dbus.service.Object.__init__(self, bus_name,
                                         '/org/gnuradio/grotarapi/controller/master')
            self.gr = GrotarAPI.GrotarAPIMaster(self, self.verbose)
            self.mm = ModuleManager.ModuleManager(mod_path = mod_path+'/master', verbose = verbose)
            self.mm_slave = ModuleManager.ModuleManager(mod_path = mod_path+'/slave', verbose = verbose)
        else:
            dbus.service.Object.__init__(self, bus_name, '/org/gnuradio/grotarapi/controller/slave')
            self.gr = GrotarAPI.GrotarAPISlave(self, self.verbose)
            self.mm = ModuleManager.ModuleManager(mod_path = mod_path+'/slave', verbose = verbose)
        self.cur_module = None
        self.cur_module_name = ''

    def request_run_module(self, module, args = None):
        self.gr.request_run_module(module, args)
        return False

    def have_module(self, module):
        if module in self.mm.get_module_list():
            return True
        else: return False

    def reset(self):
        gobject.timeout_add(400, self.stop_module)
        gobject.timeout_add(550, self.start_module, 'default')

    def have_all(self, modlist):
        if len(self.mm.get_missing(modlist)):
            return False
        else: return True

    def get_missing(self, modlist):
        return self.mm.get_missing(modlist)

    @dbus.service.method('org.gnuradio.grotarapi')
    def get_module_list(self):
        return self.mm.get_module_list()

    @dbus.service.method('org.gnuradio.grotarapi')
    def get_current_module(self):
        return self.cur_module_name

    def new_module(self, name, sha1, binary):
        return self.mm.add_module(name = name, sha1 = sha1, binary = binary, verbose=True)

    def start_module(self, module = None, args = None):
        if self.cur_module is not None:
            self.stop_module()

        if module in self.mm.get_module_list():
            if self.verbose:
                print '[INFO] CONTROLLER: Trying to start module:', self.mm.modules[module].path
                self.cur_module = subprocess.Popen(shlex.split('python ' + str(self.mm.modules[module].path)),
                                                      stdout =None,
                                                      stdin = None,
                                                      stderr= None,
                                                      preexec_fn=os.setsid)
            else:
                self.cur_module = subprocess.Popen(shlex.split('python ' + str(self.mm.modules[module].path)),
                                                      stdout = subprocess.PIPE,
                                                      stdin = None,
                                                      stderr = subprocess.PIPE,
                                                      preexec_fn=os.setsid)
                print "[INFO] CONTROLLER: Started MODULE '%s' with pid %u" % (module, self.cur_module.pid)

            if args is not None:
                if args.has_key('Time'):
                    if self.verbose:
                        print "[DEBUG] adding timeout to terminate waveform %s in %u seconds" % (module, args['Time'])
                    gobject.timeout_add_seconds(args['Time'], self.reset)
            self.cur_module_name = module
            # Emit a dbus signal to notify about the changed module
            self.module_changed(module)
        else:
            print "[INFO] CONTROLLER: We don't have %s" % module
            raise RuntimeError("We don't have module %s") % module
        return False

    def stop_module(self):
        #self.cur_module.terminate()
        #self.cur_module.kill()
        if self.verbose:
            print '[DEBUG] trying to kill child', self.cur_module.pid
        os.killpg(self.cur_module.pid, signal.SIGKILL)
        self.cur_module = None
        return False

    def request_shutdown(self):
        self.send_data('SHUTDOWN')
        gobject.timeout_add_seconds(2, self.stop_module)
        gobject.timeout_add_seconds(3, sys.exit(0))

    @dbus.service.method('org.gnuradio.grotarapi.guts', in_signature='s')
    def rx_callback_binary(self, data):
        self.gr.rx_handler(data)

    @dbus.service.signal('org.gnuradio.grotarapi.guts', signature='s')
    def send_data(self, data):
        pass

    @dbus.service.signal('org.gnuradio.grotarapi', signature='s')
    def module_changed(self, module_name):
        pass

    @dbus.service.method('org.gnuradio.grotarapi', in_signature = 'si')
    def request_run_module_dbus(self, module, arg_time):
        args = {'Time' : int(arg_time)}
        self.gr.request_run_module(module, args)
