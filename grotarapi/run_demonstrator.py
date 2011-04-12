#!/usr/bin/env python

import argparse
import Controller
import os
import gobject

def main():
    parser = argparse.ArgumentParser(description = "Run the GROTARAPI demonstrator.",
                                     epilog = "Easy, isn't it?")
    parser.add_argument('-m',
                        '--master', 
                        action = 'store_true',
                        help = 'run master or slave terminal')
    parser.add_argument('-q',
                        '--quiet', 
                        action = 'store_true',
                        help = 'output no debug information.')
    parser.add_argument('-r',
                        '--run-module', 
                        type = str,
                        default = 'default',
                        help = "which module to run at startup. Default is 'default'")
    args = parser.parse_args()

    loop = gobject.MainLoop()
    gobject.threads_init()
    print "[INFO] Starting Controller with pid %u" % os.getpid()
    myController = Controller.Controller(verbose = not args.quiet, master = args.master)
    print "[INFO] available on dbus at '/org/gnuradio/grotarapi/%s'" % ('master' if args.master else 'slave')
    myController.start_module(args.run_module)
    loop.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
