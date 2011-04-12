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

import os
import hashlib

class Module(object):
    def __init__(self, name = None, path = None, binary = None, verbose = False):
        self.name = name
        self.path = path
        if binary is None:
            f = open(path,'r')
            self.binary = f.read()
            f.close()
        else:
            self.binary = binary
            f = open(path,'w')
            f.write(self.binary)
            f.close()
        
        self.size = len(self.binary)
        self.sha1 = hashlib.sha1(self.binary).hexdigest()

        #if verbose:
            #self.print_infos()
       
    def print_infos(self):
        print "[ModuleManager] New module:"
        print "Name: %s" % self.name
        print "Path: %s" % self.path
        print "Size: %d bytes" % self.size 
        print "Hash: %s\n" % self.sha1


class ModuleManager(object):
    def __init__(self, mod_path = 'modules', verbose = False):
        self.modules = dict()
        self.mod_path = mod_path
        self.verbose = verbose
        self.reload_module_list()

    def reload_module_list(self):
        for m in os.listdir(self.mod_path):
            name, extension = os.path.splitext(m)
            if extension == '.py' and name != "__init__":
                self.modules[name] = Module(name = name,
                                            path = os.path.join(self.mod_path,m),
                                            verbose = self.verbose)
    def get_module_list(self):
        ret = list()
        for m in self.modules:
            ret.append(m)
        return ret

    def get_missing(self, modules):
        missing = list()
        for m in modules:
            if m not in self.modules:
                missing.append(m)
        return missing

    def add_module(self, name = None, path = None, binary = None, sha1 = None, verbose = False):
        if path is None:
            path = self.mod_path + '/' + name + '.py'
        mod = Module(name = name, path = path, binary = binary, verbose = verbose)
        if mod.name in self.modules:
            print '[ModuleManager] We already have the module - should not happen'
            if mod.sha1 == self.modules[mod.name].sha1 : print 'Hash ok anyway ...'
        else:
            self.modules[mod.name] = mod
            print '[ModuleManager] Adding module %s' % mod.name

        if sha1 is not None and sha1 != mod.sha1:
            return False
        else: return True
