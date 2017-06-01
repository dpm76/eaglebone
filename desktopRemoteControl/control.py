# -*- coding: utf-8 -*-

'''
Created on 10/05/2015

@author: david
'''
import sys

if sys.version_info.major < 3:
    from Tkinter import Tk
else:
    from tkinter import Tk
    
import argparse

from cockpit import Cockpit


def main(isDummy, droneIp, dronePort):

    root = Tk()
    root.geometry()
    app = Cockpit(root, isDummy=isDummy, droneIp=droneIp, dronePort=dronePort)
    root.mainloop()
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Simple control for drone")
    parser.add_argument("-d", "--dummy", action="store_true",\
                        help="Dummy mode. It doesn't send anything, and the ouput will be shown at the console.")
    parser.add_argument("-i", "--ip", help="Drone IP.", nargs="?", default=Cockpit.DEFAULT_DRONE_IP)
    parser.add_argument("-p", "--port", help="Drone port.", nargs="?", default=Cockpit.DEFAULT_DRONE_PORT, type=int)
   
    args = parser.parse_args()
    
    main(args.dummy, args.ip, args.port)
