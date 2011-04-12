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

import gobject
import cPickle as pickle
import sys

class GrotarAPI(object):
    def __init__(self, controller, verbose = False):
        self.controller = controller
        self.state = 'IDLE'
        self.verbose = verbose

    def send_data(self, data):
        self.controller.send_data(data)

    def rx_handler(self, data):
        pass

class GrotarAPIMaster(GrotarAPI):
    def __init__(self, controller, verbose = False):
        GrotarAPI.__init__(self, controller, verbose)
        self.state = 'IDLE'
        self.module_to_run = None
        self.params_to_run = None

    def rx_handler(self, data):
        if not data.strip() == 'ERROR':
            if self.state is 'IDLE':
                if self.verbose:
                    print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)

            elif self.state is 'WAIT_FOR_RUN_ACK':
                if data.strip() == 'RUN_ACK':
                    if self.verbose:
                        print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)
                    gobject.timeout_add(400, self.controller.stop_module)
                    gobject.timeout_add(550, self.controller.start_module, self.module_to_run, self.params_to_run)
                    self.state = 'IDLE'

                elif data.strip() == 'RUN_NAK':

                    if self.verbose:
                        print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)

                    self.send_data('MODLIST_BEGIN')
                    for i in self.controller.get_module_list():
                        self.send_data(i)
                    self.send_data('MODLIST_FINISH')
                    self.state = 'WAIT_FOR_MODLIST_ACK'
                else:
                    self.send_data('ERROR')
                    self.controller.reset()

            elif self.state is 'WAIT_FOR_MODLIST_ACK':
                if data.strip() == 'MODLIST_ACK':
                    if self.verbose:
                        print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)
                    if self.module_to_run is not None:
                        self.send_data('RUN_MOD')
                        self.send_data(self.module_to_run)
                        if self.params_to_run is None:
                            self.send_data('ARGS_NONE')
                        else:
                            self.send_data(pickle.dumps(self.params_to_run))
                        self.state = 'IDLE'
                        gobject.timeout_add(300, self.controller.start_module, self.module_to_run, self.params_to_run)
                    else:
                        gobject.timeout_add(300, self.controller.start_module, 'default')

                elif data.strip() == 'MISSING':
                    if self.verbose:
                        print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)
                    self.state = 'WAIT_FOR_MISSING_NAME'

                else:
                    self.send_data('ERROR')
                    self.controller.reset()

            elif self.state is 'WAIT_FOR_MISSING_NAME':
                if self.verbose:
                    print '[DEBUG] GROTARAPI MASTER(%s): received %s' % (self.state, data)

                module = self.controller.mm_slave.modules[data.strip()]
                self.send_data(module.name)
                signed_module = self.controller.gpg.sign(module.binary, clearsign=False)
                self.send_data(str(len(signed_module.data)))
                self.send_data(module.sha1)

                blocks = len(signed_module.data) / 1536
                leftover = len(signed_module.data) % 1536

                if self.verbose:
                    print '[DEBUG] GROTARAPI MASTER(%s): sending %u blocks with %u leftover' % (
                           self.state ,blocks, leftover)

                for i in range(blocks):
                    if self.verbose:
                        print '[DEBUG] GROTARAPI MASTER(%s): sending block %u out of %u' % (self.state,
                                                                                            i, blocks)
                    self.send_data(signed_module.data[i*1536:(i*1536)+1536])

                self.send_data(signed_module.data[-leftover:])
                self.state = 'WAIT_FOR_MODLIST_ACK'

            else:
                self.send_data('ERROR')
                self.controller.reset()
                        

    def request_run_module(self, mod_name, args = None):
        self.send_data('RUN_MOD')
        self.send_data(mod_name)
        if args is None:
            self.send_data('ARGS_NONE')
        else:
            self.send_data(pickle.dumps(args))
        self.state = 'WAIT_FOR_RUN_ACK'
        self.module_to_run = mod_name
        self.params_to_run = args

class GrotarAPISlave(GrotarAPI):
    def __init__(self, controller, verbose = True):
        GrotarAPI.__init__(self, controller, verbose)
        self.module_to_run = None
        self.mod_to_run_params = ''
        self.modlist_received = list()
        self.mod_buffer = dict()
        self._flush_mod_buffer()
        
    def _flush_mod_buffer(self):
        self.mod_buffer['NAME'] = ''
        self.mod_buffer['LEN'] = 0
        self.mod_buffer['HASH'] = ''
        self.mod_buffer['BINARY'] = ''



    def rx_handler(self, data):
        if (self.state != 'WAIT_FOR_MODULE_BINARY' and data.strip() == 'ERROR'):
            self.state = 'IDLE'
            self.send_data('ERROR')
            self.controller.reset()

        if self.state is 'IDLE':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)

            if data.strip() == 'RUN_MOD':
                self.state = 'WAIT_FOR_RUN_NAME'

            elif data.strip() == 'SHUTDOWN':
                gobject.timeout_add(500, self.controller.stop_module)
                gobject.timeout_add(800, sys.exit, 0)
            else:
                self.state = 'IDLE'

        elif self.state is 'WAIT_FOR_RUN_NAME':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)
            self.module_to_run = data.strip()
            self.state = 'WAIT_FOR_ARGS'

        elif self.state is 'WAIT_FOR_ARGS':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)
            if data.strip() =='ARGS_NONE':
                self.mod_to_run_params = None
            else:
                self.mod_to_run_params = pickle.loads(str(data))

            if self.controller.have_module(self.module_to_run):
                self.send_data('RUN_ACK')
                #Give some time to send the RUN_ACK
                gobject.timeout_add(400, self.controller.stop_module)
                gobject.timeout_add(500, self.controller.start_module, self.module_to_run, self.mod_to_run_params)
                self.state = 'IDLE'
            else:
                self.send_data('RUN_NAK')
                self.state = 'WAIT_FOR_MODLIST_BEGIN'

        elif self.state is 'WAIT_FOR_MODULE_NAME':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)
            self.mod_buffer['NAME'] = data.strip()
            self.state = 'WAIT_FOR_MODULE_LEN'

        elif self.state is 'WAIT_FOR_MODULE_LEN':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)
            self.mod_buffer['LEN'] = int(data.strip())
            self.state = 'WAIT_FOR_MODULE_HASH'

        elif self.state is 'WAIT_FOR_MODULE_HASH':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)

            self.mod_buffer['HASH'] = data.strip()
            self.state = 'WAIT_FOR_MODULE_BINARY'

        elif self.state is 'WAIT_FOR_MODULE_BINARY':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %u bytes' % (self.state, len(data))

            if len(data) <= (self.mod_buffer['LEN'] - len(self.mod_buffer['BINARY'])):
                self.mod_buffer['BINARY'] += data

            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): wrote %u bytes to self.mod_buffer' % (self.state, len(self.mod_buffer['BINARY']))

            if len(self.mod_buffer['BINARY']) == self.mod_buffer['LEN']:
                try:
                    module_binary = self.controller.gpg.decrypt(self.mod_buffer['BINARY'])
                    matched = self.controller.new_module(name = self.mod_buffer['NAME'],
                                           sha1 = self.mod_buffer['HASH'], 
                                           binary = module_binary.data)
                except ValueError:
                    print '[DEBUG] something went wrong in extracting the data from the signed stuff'
                
                self._flush_mod_buffer()

                if self.verbose:
                    print '[DEBUG] GROTARAPI SLAVE(%s): Hash matched: ' % self.state , matched

                if self.controller.have_all(self.modlist_received):
                    self.state = 'IDLE'
                    self.send_data('MODLIST_ACK')
                else:
                    self.send_data('MISSING')
                    self.send_data(self.controller.get_missing(self.modlist_received)[0])
                    self.state = 'WAIT_FOR_MODULE_NAME'

        elif self.state is 'WAIT_FOR_MODLIST_BEGIN':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)

            if data.strip() == 'MODLIST_BEGIN':
                self.state = 'WAIT_FOR_MODLIST_ELEM'

        elif self.state is 'WAIT_FOR_MODLIST_ELEM':
            if self.verbose:
                print '[DEBUG] GROTARAPI SLAVE(%s): received %s' % (self.state, data)

            if data.strip() != 'MODLIST_FINISH':
                self.modlist_received.append(data.strip())
            else:
                if self.controller.have_all(self.modlist_received):
                    self.send_data('MODLIST_ACK')
                    self.state = 'IDLE'
                else:
                    self.send_data('MISSING')
                    self.send_data(self.controller.get_missing(self.modlist_received)[0])
                    self.state = 'WAIT_FOR_MODULE_NAME'
