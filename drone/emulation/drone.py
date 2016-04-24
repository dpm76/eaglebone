# -*- coding: utf-8 -*-

'''
Created on 03/02/2016

@author: david
'''

from operator import add
import time

from emulation.propeller import Propeller
from emulation.state import State
from math import pi as PI
from copy import deepcopy



class EmulatedDrone(object):
    '''
    Emulates a physical drone
    '''
    
    #Realistic or ideal flight emulation mode
    REALISTIC_FLIGHT = True
    
    #TODO Create config
    PROPELLER_THRUST_RATE = 0.01 # 1.0kg @100%
    PROPELLER_COUNTER_ROTATION_RATE = 10.0    
    WEIGHT = 1.8 # kg
    MAX_CRASH_SPEED = -1.0 #m/s
    ARM_LENGTH = 0.23 #m
    
    _instance = None
    
    @staticmethod
    def getInstance():
        
        if EmulatedDrone._instance == None:
            EmulatedDrone._instance = EmulatedDrone()
            
        return EmulatedDrone._instance
    

    def __init__(self):
        
        self._state = State()
        self._weight = EmulatedDrone.WEIGHT        
        self._armLength = EmulatedDrone.ARM_LENGTH        
        self._arcSpeedToAngleSpeed = 180.0/PI*self._armLength
        
        if EmulatedDrone.REALISTIC_FLIGHT:
        
            self._propellers = [Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.94, 1.0 * self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.91, 0.6 * self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.85, 1.0 * self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.95, 1.4 * self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE)]
        else:
            
            self._propellers = [Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 1.0, self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 1.0, self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 1.0, self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 1.0, self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE)]

        self._propellersCount = len(self._propellers)

        self._propellersUpdatedCount = 0
        
    
    def getPropeller(self, index):
        
        return self._propellers[index]
    
    
    def _updateStatus(self):
        
        if self._state._time and not self._state._crashed:
            
            currentTime = time.time() 
            dt = currentTime - self._state._time
            dt2 = dt/2.0
            self._state._time = currentTime
        
            #Accelerations
            
            previousAngleSpeedZ = self._state._angleSpeeds[2] 
            self._state._angleSpeeds[2] = 0.0
            
            forces = [0.0]*3            
            for propeller in self._propellers:
                            
                propellerForces = propeller.getThrust()                
                self._state._angleSpeeds[2] += propeller.getTorque()
                forces = map(add, forces, propellerForces)

            previousAccels = deepcopy(self._state._accels)
            self._state._accels = [force / self._weight for force in forces]
            
            #Speed & position
            for index in range(3):
                previousSpeed = self._state._speeds[index]
                self._state._speeds[index] += (self._state._accels[index] + previousAccels[index]) * dt2
                self._state._coords[index] += (self._state._speeds[index] + previousSpeed) * dt2
            
            #The drone can not fly underground
            if self._state._coords[2] <= 0.0 and self._state._speeds[2] <= 0.0:
                            
                self._state._crashed = self._state._speeds[2] < EmulatedDrone.MAX_CRASH_SPEED
                
                self._state._coords[2] = 0.0
                self._state._accels = [0.0]*3
                self._state._speeds = [0.0]*3
                self._state._angles = [0.0, 0.0, self._state._angles[2]]
                self._state._angleSpeeds = [0.0]*3
            
                '''    
                elif self._state._coords[2] >= 0.5 and self._state._speeds[2] > 0.0:
                    
                    self._state._coords[2] = 0.5
                    self._state._accels = [0.0]*3
                    self._state._speeds = [0.0]*3
                '''
            else:
            
                #Calculate drone's current yaw (self._state._angles[2])
                #Positive angles are CCW for axis Z
                self._state._angles[2] += (self._state._angleSpeeds[2] + previousAngleSpeedZ) * dt2           
                    
                #Calculate drone's angle-speeds
                accelAxisX = self._propellers[3].getOrtogonalAccel() - self._propellers[1].getOrtogonalAccel()
                previousAngleSpeedX = self._state._angleSpeeds[0]
                self._state._angleSpeeds[0] += accelAxisX * dt * self._arcSpeedToAngleSpeed
    
                accelAxisY = self._propellers[2].getOrtogonalAccel() - self._propellers[0].getOrtogonalAccel()
                previousAngleSpeedY = self._state._angleSpeeds[1]
                self._state._angleSpeeds[1] += accelAxisY * dt * self._arcSpeedToAngleSpeed            
    
                #Calculate drone's angles (heading was already calculated)
                self._state._angles[0] += (self._state._angleSpeeds[0] + previousAngleSpeedX) * dt2
                self._state._angles[1] += (self._state._angleSpeeds[1] + previousAngleSpeedY) * dt2                         
    
            #Update propeller angles
            for propeller in self._propellers:
                propeller.setAngles(self._state._angles)

            #if dt < 1.0:
            #    print self._state            
        
        
    def getState(self):
        
        return self._state
        
    
    def initStateTime(self):
        
        self._state._time = time.time()
        
    
    def onPropellerUpdated(self):
        
        self._propellersUpdatedCount += 1
        if self._propellersUpdatedCount == self._propellersCount:
            
            self._updateStatus()
            self._propellersUpdatedCount = 0
            
        elif self._propellersUpdatedCount > self._propellersCount:
            
            raise Exception("Error: Any propellers updated unsuccesfully.")
        
