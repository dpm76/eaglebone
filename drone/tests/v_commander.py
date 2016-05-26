# -*- coding: utf-8 -*-
'''
Created on 30/05/2015

@author: david
'''
from flight.visual_controller import VisualFlightController

controller = VisualFlightController.getInstance()
controller.start()

done = False

try:
    while not done:
    
        command = raw_input("Insert command: ").strip().split()
        if len(command) != 0:
            command0 = command[0].upper()
        else:
            command0 = ""
    
        if command0 == "QUIT" or command0 == "": #Quit
            done = True
            
        elif command0 == "TH":
            
            if len(command) == 2:
                increment = float(command[1])
                controller.addThrottle(increment)
            else:
                print "Throttle: TH increment"
        
            '''    
            elif command0 == "SH":
                
                if len(command) == 3:
                    angle = radians(float(command[1]))
                    device.shift(angle, float(command[2]))
                else:
                    print "Shift: SH degrees-angle inc-percentage"
            '''        
            '''        
            elif command0 == "SP":
                
                if len(command) == 2:
                    increment = float(command[1])
                    device.spin(increment)
                else:
                    print "Spin: SP inc-percentage"
            '''                
            
        elif command0 == "SB":            
            controller.standBy()
            
        elif command0 == "ID":
            controller.idle()            
        
        elif command0 == "+":
            controller.addThrottle(1)
            
        elif command0 == "-":
            controller.addThrottle(-1)        
            
        elif command0 == "HELP" or command0 == "?":
            print "Commands list:"
            print "\tQUIT: Stop and exit"
            print "\tTH: Throttle"
            #print "\tSH: Shift"
            #print "\tSP: Spin"
            print "\tSB: Stand-by"
            print "\tID: Idle"
            print "\t+: Add 1% throttle"
            print "\t-: Reduce 1% throttle"
            
        else:
            print "Unknown command"

finally:
    controller.stop()
    print "Goodbye!"
