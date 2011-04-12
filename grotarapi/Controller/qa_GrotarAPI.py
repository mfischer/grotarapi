#!/usr/bin/env python

import GrotarAPI
import Controller
import ModuleManager
import unittest
import os
import shutil

class TestController(Controller.Controller):
    def __init__(self, master = False):
        Controller.Controller(master = master, mod_path = '/tmp/grotarapitest', verbose = False)
        self.sent = list()
        self.cur_module = None
        if master:
            self.mm = ModuleManager.ModuleManager(mod_path = '/tmp/grotarapitest/master', verbose = True)
            self.mm_slave = ModuleManager.ModuleManager(mod_path = '/tmp/grotarapitest/slave', verbose = True)
        else:
            self.mm = ModuleManager.ModuleManager(mod_path = '/tmp/grotarapitest/slave', verbose = True)

        self.added_modules = list()

    def start_module(self, module):
        if module in self.mm.modules:
            print 'TestController started module %s' % module
            self.stop_module()
            self.cur_module = module
        else:
            raise RuntimeError("We don't have this one")

    def stop_module(self):
        print 'TestController stopped module'

    def send_data(self, data):
        self.sent.append(data)

    def new_module(self, name, sha1, binary):
        print 'TestController created a new module %s' % name
        self.added_modules.append(name)

    def have_module(self, module):
        if module in self.added_modules:
            return True

    def have_all(self, modlist):
        missing = list()
        for i in modlist:
            if i not in self.added_modules:
                missing.append(i)
        if not len(missing) : return True

    def get_missing(self, modlist):
        missing = list()
        for i in modlist:
            if i not in self.added_modules:
                missing.append(i)
        return missing

    def get_module_list(self):
        return self.mm.get_module_list()

class TestGrotarAPI(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_slave (self): 
        if os.path.exists('/tmp/grotarapitest/slave'):
            shutil.rmtree('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest/slave')
        mod = open('/tmp/grotarapitest/slave/Test3.py','wa')
        mod.write(200*'test')
        mod.close()

        tc = TestController()
        gr = GrotarAPI.GrotarAPISlave(tc)
        self.assertEqual(gr.state, 'IDLE')
        gr.rx_handler('RUN_MOD')
        self.assertEqual(gr.state, 'WAIT_FOR_RUN_NAME')
        gr.rx_handler('Test1')
        self.assertEqual(gr.state, 'WAIT_FOR_ARGS')
        gr.rx_handler('')
        self.assertEqual(tc.sent.pop(), 'RUN_NAK')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_BEGIN')
        gr.rx_handler('MODLIST_BEGIN')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ELEM')
        gr.rx_handler('Test1')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ELEM')
        gr.rx_handler('Test2')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ELEM')
        gr.rx_handler('MODLIST_FINISH')
        self.assertEqual(tc.sent.pop(), 'Test1')
        self.assertEqual(tc.sent.pop(), 'MISSING')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_NAME')
        mod_binary = os.urandom(100)
        gr.rx_handler('Test1')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_LEN')
        gr.rx_handler(str(len(mod_binary)))
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_HASH')
        self.assertEqual(gr.mod_buffer['LEN'], len(mod_binary))
        gr.rx_handler('0xdeadbeef')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_BINARY')
        gr.rx_handler(mod_binary)
        self.assertEqual(tc.sent.pop(), 'Test2')
        self.assertEqual(tc.sent.pop(), 'MISSING')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_NAME')
        gr.rx_handler('Test2')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_LEN')
        gr.rx_handler('200')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_HASH')
        gr.rx_handler('0xdeadbeef')
        self.assertEqual(gr.state, 'WAIT_FOR_MODULE_BINARY')
        gr.rx_handler(200*'1')
        self.assertEqual(gr.state, 'IDLE')

    def test_master_simple (self):
        if os.path.exists('/tmp/grotarapitest'):
            shutil.rmtree('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest/slave')
        mod = open('/tmp/grotarapitest/slave/Test3.py','wa')
        mod.write("if __name__ == '__main__':\n    print 'Running Test3 Module")
        mod.close()

        tc = TestController()
        gr = GrotarAPI.GrotarAPIMaster(tc)
        self.assertEqual(gr.state, 'IDLE')
        gr.request_run_module('Test3')
        self.assertEqual(tc.sent.pop(), ' ')
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(tc.sent.pop(), 'RUN_MOD')
        self.assertEqual(gr.state, 'WAIT_FOR_RUN_ACK')
        gr.rx_handler('RUN_ACK')
        self.assertEqual(gr.state, 'IDLE')

    def test_master_modlist (self):
        if os.path.exists('/tmp/grotarapitest/slave'):
            shutil.rmtree('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest/slave')
        mod = open('/tmp/grotarapitest/slave/Test3.py','wa')
        mod.write("if __name__ == '__main__':\n    print 'Running Test3 Module")
        mod.close()
    
        tc = TestController()
        gr = GrotarAPI.GrotarAPIMaster(tc)
        self.assertEqual(gr.state, 'IDLE')
        gr.request_run_module('Test3')
        self.assertEqual(tc.sent.pop(), '')
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(tc.sent.pop(), 'RUN_MOD')
        self.assertEqual(gr.state, 'WAIT_FOR_RUN_ACK')
        gr.rx_handler('RUN_NAK')
        self.assertEqual(tc.sent.pop(), 'MODLIST_FINISH')
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(tc.sent.pop(), 'MODLIST_BEGIN')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ACK')
        gr.rx_handler('MODLIST_ACK')
        self.assertEqual(gr.state, 'IDLE')

    def test_master_modlist (self):
        if os.path.exists('/tmp/grotarapitest/slave'):
            shutil.rmtree('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest')
        os.mkdir('/tmp/grotarapitest/slave')
        mod = open('/tmp/grotarapitest/slave/Test3.py','wa')
        mod.write(200*'test')
        mod.close()

        tc = TestController()
        gr = GrotarAPI.GrotarAPIMaster(tc)
        self.assertEqual(gr.state, 'IDLE')
        gr.request_run_module('Test3')
        self.assertEqual(gr.module_to_run, 'Test3')
        self.assertEqual(tc.sent.pop(), ' ')
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(tc.sent.pop(), 'RUN_MOD')
        self.assertEqual(gr.state, 'WAIT_FOR_RUN_ACK')
        gr.rx_handler('RUN_NAK')
        self.assertEqual(tc.sent.pop(), 'MODLIST_FINISH')
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(tc.sent.pop(), 'MODLIST_BEGIN')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ACK')
        gr.rx_handler('MISSING')
        self.assertEqual(gr.state, 'WAIT_FOR_MISSING_NAME')
        gr.rx_handler('Test3')
        self.assertEqual(tc.sent.pop(), 200*'test')
        tc.sent.pop()
        self.assertEqual(tc.sent.pop(), str(len(200*'test')))
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ACK')
        gr.rx_handler('MISSING')
        self.assertEqual(gr.state, 'WAIT_FOR_MISSING_NAME')
        gr.rx_handler('Test3')
        self.assertEqual(tc.sent.pop(), 200*'test')
        tc.sent.pop()
        self.assertEqual(tc.sent.pop(), str(len(200*'test')))
        self.assertEqual(tc.sent.pop(), 'Test3')
        self.assertEqual(gr.state, 'WAIT_FOR_MODLIST_ACK')
        gr.rx_handler('MODLIST_ACK')

if __name__ == '__main__':
    unittest.main ()

