# -*- coding: utf-8 -*-

'''
Created on 03/02/2016

@author: david
'''
from math import radians
from sensors.vector import Vector


class Propeller(object):
    '''
    Represents the drone's propeller
    '''
    
    THROTTLE_THRESHOLD = 10.0 #Below this threshold the motor cannot move the propeller
    LPF = 0.9 #Low-pass filter threshold
    
    GRAVITY = 9.807 #m/s²
    
    ROTATION_CW = 0
    ROTATION_CCW = 1

    def __init__(self, drone, rotationThrustRate, throttleRotationRate, thrustedWeight, rotation, counterRotationRate):
        '''
        Constructor
        
        @param drone: Drone object to notify changes  
        @param rotationThrustRate: Rate of thrust increment per angular-speed. 
            For example: let a propeller of max. 4kg. This means that 100% angular-speed is 4kg thrust, 
            then the rate is 0.04
        @param throttleRotationRate: Rate of rotation per throttle. Simulates the power down due to the presence
            of the other propellers. Should be near to 1.0
        @param thrustedWeight: Weight that this propeller carries
        @param rotation: Rotation mode (clockwise/counter clockwise)
        @param counterRotationRate: Reaction rotation to the current rotation
        '''

        self._throttleThrustRate = rotationThrustRate * throttleRotationRate
        self._thrustedWeight = thrustedWeight
        
        #IMU's positive angles are CCW
        if rotation == Propeller.ROTATION_CW:
            self._counterRotationRate = counterRotationRate
        else:
            self._counterRotationRate = -counterRotationRate

        self._throttle = 0.0
        self._thrustModule = 0.0
        self._thrust = [0.0]*3
        
        self._angles = [0.0] * 3
        
        self._drone = drone
        
        self._lowPassFilter = Propeller.LPF if self._drone._realisticFlight else 1.0
    
    
    def getWeight(self):
        
        return self._thrustedWeight
    
    
    def setThrottle(self, throttle):
        '''
        Set the throttle
        
        @param throttle: Percentage of the throttle        
        '''
        
        self._throttle = throttle
        self._update()

        
    def setAngles(self, angles):
        '''
        Set the angles

        @param angles: Angles as degrees of the propeller
        '''

        self._angles = [radians(angle) for angle in angles]

    
    def getThrust(self):
        
        return self._thrust
    
    
    def getTorque(self):
        
        return self._counterRotation
    
    
    def getThrottle(self):
        
        return self._throttle


    def getOrtogonalAccel(self):
        
        return self._throttle * self._throttleThrustRate * Propeller.GRAVITY / self._thrustedWeight
    
    
    def _update(self):

        effectiveThrottle = self._throttle - Propeller.THROTTLE_THRESHOLD \
            if self._throttle > Propeller.THROTTLE_THRESHOLD else 0.0        

        newThrustModule = effectiveThrottle * self._throttleThrustRate * Propeller.GRAVITY
        self._thrustModule += self._lowPassFilter * (newThrustModule - self._thrustModule) 
        self._thrust = Vector.rotateVector3D([0.0, 0.0, self._thrustModule], self._angles)
        self._thrust[2] -= Propeller.GRAVITY * self._thrustedWeight

        #Counter-rotation        
        self._counterRotation = self._thrustModule * self._counterRotationRate
    
        self._drone.onPropellerUpdated()
