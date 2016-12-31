# -*- coding: utf-8 -*-

'''
Created on 06/04/2015

@author: david
'''

import logging
from os import system
from os.path import exists
import sys
from threading import Lock

from config import Configuration
from flight.driving.motor import Motor
from flight.driving.motor_dummy import MotorDummy
from emulation.motor import EmulatedMotor


class Driver(object):
    '''
    Controls a motor set
    '''
    
    NUM_MOTORS = 4
    
    def __init__(self, motorType=""):
        '''
        Constructor

        @param motorType: String with the type of the motor to implement. See Configuration.VALUE_MOTOR_CLASS_*
        If motorType value is not provided, the configuration will be used.
        '''
        
        self._lock = Lock()
        
        self._config = Configuration.getInstance().getConfig()        
        self._motors = []
        self._baseThrottle = 0.0
        self._motorIncrements = [0.0] * Driver.NUM_MOTORS

        if motorType == "":
            motorType = self._config[Configuration.KEY_MOTOR_CLASS]

        for motorId in range(Driver.NUM_MOTORS):
            motor = self._createMotor(motorId, motorType)
            self._motors.append(motor)            
            
    
    def _createMotor(self, motorId, motorClass):
        '''
        Creates a new motor instance
        '''
        
        if motorClass == Configuration.VALUE_MOTOR_CLASS_LOCAL:
            motor = Motor(motorId)
            self._maxMotorThrottle = Motor.MAX_THROTTLE
            
        elif motorClass == Configuration.VALUE_MOTOR_CLASS_REMOTE:
            #TODO deprecated: this feature won't be implemented
            message = "Remote motor will not be implemented!"
            print message
            logging.fatal(message)
            sys.exit()
            
        elif motorClass == Configuration.VALUE_MOTOR_CLASS_EMULATION:
            motor = EmulatedMotor(motorId)
            self._maxMotorThrottle = EmulatedMotor.MAX_THROTTLE
            
        else: #default VALUE_MOTOR_CLASS_DUMMY
            motor = MotorDummy(motorId)        
            self._maxMotorThrottle = MotorDummy.MAX_THROTTLE            
            
        return motor
            
        
    def start(self):
        '''
        Inits the motor set
        '''
        
        if self._config[Configuration.KEY_MOTOR_CLASS] == Configuration.VALUE_MOTOR_CLASS_LOCAL \
            and not exists("/sys/class/pwm/pwm3"):
            
            system("echo cape-universaln > /sys/devices/bone_capemgr.*/slots")
            
        #Init motors
        with self._lock:
            self._baseThrottle = 0.0
            for motor in self._motors:
                motor.start()
            
            
    def standBy(self):
        
        with self._lock:
            self._baseThrottle = 0.0
            self._motorIncrements = [0.0] * Driver.NUM_MOTORS
            for motor in self._motors:
                motor.standBy()
            
            
    def idle(self):
        
        with self._lock:
            self._baseThrottle = 0.0
            self._motorIncrements = [0.0] * Driver.NUM_MOTORS
            for motor in self._motors:
                motor.idle()
            
            
    def stop(self):

        with self._lock:        
            self._baseThrottle = 0.0
            self._motorIncrements = [0.0] * Driver.NUM_MOTORS
            for motor in self._motors:
                motor.stop()
            
            
    def addThrottle(self, increment):

        with self._lock:
            self._baseThrottle += increment
            #for motor in self._motors:
            #    motor.addThrottle(increment)            
                        
    
    def shiftX(self, increment): 
        
        with self._lock:
            self._motorIncrements[0] += -increment
            #self._motorIncrements[1] += -increment

            self._motorIncrements[2] += increment
            #self._motorIncrements[3] += increment

    
    def shiftY(self, increment):
    
        with self._lock:
            #self._motorIncrements[0] += -increment
            self._motorIncrements[3] += -increment
        
            self._motorIncrements[1] += increment
            #self._motorIncrements[2] += increment


    def spin(self, increment): 
        
        with self._lock:
   
            self._motorIncrements[0] += -increment
            self._motorIncrements[2] += -increment

            self._motorIncrements[1] += increment
            self._motorIncrements[3] += increment


    def commitIncrements(self):

        with self._lock:
            try:
                for index in range(Driver.NUM_MOTORS):
                    increment = self._motorIncrements[index]                    
                    self._motors[index].setThrottle(self._baseThrottle + increment)
                        
            except Exception as ex:
                logging.warning("Driver commit exception: {0}".format(str(ex)))
                
            finally:
                self._motorIncrements = [0.0] * Driver.NUM_MOTORS
                
                
    def getThrottles(self):
        
        return [motor.getThrottle() for motor in self._motors]
    
    
    def getBaseThrottle(self):
        
        return self._baseThrottle
    
    
    def setThrottle(self, throttle):

        with self._lock:
            self._baseThrottle = throttle
            for motor in self._motors:
                motor.setThrottle(throttle)

            