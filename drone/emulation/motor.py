# -*- coding: utf-8 -*-

'''
Created on 7 de feb. de 2016

@author: david
'''
from emulation.drone import EmulatedDrone


class EmulatedMotor(object):
    '''
    Motor of the emulated drone
    Adapter of the propeller's interface for the driver object
    '''
    
    MAX_THROTTLE = 80.0
    
    def __init__(self, motorId):
        """
        Constructor
        
        @param motorId: Identificator of the motor. A number between 0 to 3 (in case of quadcopter)  
        """
        
        self._throttle = 0.0
        self._propeller = EmulatedDrone.getInstance().getPropeller(motorId)        
        
        
    def start(self):
        
        self.setThrottle(0.0)
        
    
    def setThrottle(self, throttle):
        
        self._throttle = throttle
        
        if self._throttle < 0.0:
            self._propeller.setThrottle(0.0)

        elif self._throttle > EmulatedMotor.MAX_THROTTLE:
            self._propeller.setThrottle(EmulatedMotor.MAX_THROTTLE)

        else:
            self._propeller.setThrottle(throttle)        

        
    def getThrottle(self):
        
        return self._throttle
    

    def getPropellerThrottle(self):

        return self._propeller.getThrottle()

    
    def addThrottle(self, increment):
        """
        Increases or decreases the motor's throttle
        
        @param increment: Value added to the current throttle percentage. This can be negative to decrease.
        """
        
        self.setThrottle(self.getThrottle() + increment)
        
    
    def setMaxThrottle(self):
        """
        Sends the max throttle signal (useful for calibrating process)
        """

        self.setThrottle(100.0)
        
        
    def setMinThrottle(self):
        """
        Sends the min throttle signal (useful for calibrating process, or setting the motor in stand-by state)
        """
        
        self.setThrottle(0.0)
        
        
    def standBy(self):
        """
        Set the motor in stand-by state
        """
        
        self.setMinThrottle()        
        
        
    def idle(self):
        """
        Set the motor in idle state
        """
        
        self.setThrottle(0.0)
        
        
    def stop(self):
        """
        Stops the motor
        """
        
        self.setThrottle(0.0)
