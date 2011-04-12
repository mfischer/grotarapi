#!/usr/bin/env python2
import unittest
import struct
import os
import shutil
import ModuleManager

class TestModuleManager(unittest.TestCase):
    def setUp(self):
        try:
            os.mkdir('/tmp/module_test')
        except OSError:
            shutil.rmtree('/tmp/module_test')
            os.mkdir('/tmp/module_test')
        self.mm = ModuleManager.ModuleManager(mod_path = '/tmp/module_test', verbose = False)

    def tearDown(self):
        shutil.rmtree('/tmp/module_test')

    def test_simple (self): 
        mm = self.mm
        self.assertEqual(len(mm.get_module_list()), 0)
        f = open('qa_module_manager.py')
        binary = f.read()
        mm.add_module(name = 'qa_module_manager', binary = binary, path ='/tmp/module_test/qa_module_manager.py')
        self.assertEqual(len(mm.get_module_list()), 1)
        self.assertTrue(os.path.exists('/tmp/module_test/qa_module_manager.py'))
        self.assertEqual(mm.modules['qa_module_manager'].size, len(binary))

    def test_reload_modules_dir (self):
        mm = self.mm
        self.assertEqual(len(mm.get_module_list()), 0)
        f = open('/tmp/module_test/foobar.py','w')
        f.write('Module Test Content for Module1')
        f.close()
        f = open('/tmp/module_test/foobar2.py','w')
        f.write('Module Test Content for Module2')
        f.close()
        mm.reload_module_list()
        self.assertEqual(len(mm.get_module_list()), 2)
 
if __name__ == '__main__':
    unittest.main ()
    
