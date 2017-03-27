# -*- coding: utf-8 -*-

'''
Created on 7 de feb. de 2016

@author: david
'''
import logging

from emulation.drone import EmulatedDrone
from random import uniform, seed
from copy import deepcopy


class EmulatedSensor(object):
    '''
    IMU sensor of the emulated drone
    '''
    
    ERROR_ANGLE_SPEED_DISTRIBUTION = [-1.0, 1.0] #[-0.1, 0.15]
    ERROR_ANGLE_DISTRIBUTION = [-0.0, 0.0] #[-0.08, 0.1]
    ERROR_ACCEL_DISTRIBUTION = [-0.1, 0.1] #[-0.1, 0.15]
    
    def __init__(self, addNoise):
        
        self._addNoise = addNoise
        if self._addNoise:        
            seed()
        self._drone = EmulatedDrone.getInstance()
    
    
    def _noisify(self, data, distribution):

        inputData = deepcopy(data)
        noisedList = [item + uniform(distribution[0], distribution[1]) for item in inputData]

        return noisedList


    def readAngleSpeeds(self):
        '''
        Positive angles are CCW for axis Z
        '''
        
        state = self._drone.getState()        

        angleSpeeds = \
            self._noisify(state._angleSpeeds, EmulatedSensor.ERROR_ANGLE_SPEED_DISTRIBUTION) \
            if self._addNoise \
            else deepcopy(state._angleSpeeds)
            
        return angleSpeeds 

    
    def readAngles(self):
        '''
        Positive angles are CCW for axis Z
        '''
        
        state = self._drone.getState()        
        angles = \
            self._noisify(state._angles, EmulatedSensor.ERROR_ANGLE_DISTRIBUTION) \
            if self._addNoise \
            else deepcopy(state._angles) 
        
        return angles

    
    def readDeviceAngles(self):

        return self.readAngles()


    def readAccels(self):
        
        state = self._drone.getState()        
        accels = \
            self._noisify(state._accels, EmulatedSensor.ERROR_ACCEL_DISTRIBUTION) \
            if self._addNoise \
            else deepcopy(state._accels)
        
        return accels

    
    def resetGyroReadTime(self):
        
        self._drone.initStateTime()

    
    def refreshState(self):
        pass
    
    
    def start(self):
        
        text = "Using emulated drone's IMU." 

        print(text)
        logging.info(text)
        
    
    def calibrate(self):
        pass
    
    def stop(self):
        pass
    
    def getMaxErrorZ(self):
        
        return EmulatedSensor.ERROR_ACCEL_DISTRIBUTION[1]
    