# -*- coding: utf-8 -*-

'''
Created on 03/02/2016

@author: david
'''

from copy import deepcopy
from math import pi as PI, sin, radians, sqrt, asin, degrees
from operator import add
import time

from emulation.propeller import Propeller
from emulation.state import State


class EmulatedDrone(object):
    '''
    Emulates a physical drone
    '''
    
    #TODO Create config
    REALISTIC_FLIGHT = True #Realistic or ideal flight emulation mode
    HANGED_MODE = False #Emulates the drone hanged by ropes. It doesn't move, but speeds and accelerations changes.
    X_CONFIGURATON = False # Indicates whether the drone is configured as X or + 
    PROPELLER_THRUST_RATE = 0.0075 # 0.75kg/propeller @100% (total x4 propellers: 3.0kg max. thrust)
    PROPELLER_COUNTER_ROTATION_RATE = 1000.0    
    WEIGHT = 1.6 # kg
    MAX_CRASH_SPEED = -1.0 #m/s
    ARM_LENGTH = 0.23 #m    
    #end config
    
    R1 = sqrt(2.0)/2.0 # constant used for angle rotation in X-configuration mode
    
    _instance = None
    
    @staticmethod
    def getInstance():
        
        if EmulatedDrone._instance == None:
            EmulatedDrone._instance = EmulatedDrone()
            
        return EmulatedDrone._instance
    

    def __init__(self):
        
        self._realisticFlight = EmulatedDrone.REALISTIC_FLIGHT 
        
        self._state = State()
        if EmulatedDrone.X_CONFIGURATON:
            self._state._angles = [0.0, 0.0, -45.0]

        if EmulatedDrone.HANGED_MODE:
            self._state._coords = [0.0, 0.0, 1.0]            
            
        self._weight = EmulatedDrone.WEIGHT        
        self._armLength = EmulatedDrone.ARM_LENGTH        
        self._arcSpeedToAngleSpeed = 180.0/PI*self._armLength
        
        if self._realisticFlight:
        
            self._propellers = [Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.98, 1.01 * self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.97, 0.97 * self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.96, 0.99 * self._weight/4.0, Propeller.ROTATION_CW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE),
                                Propeller(self, EmulatedDrone.PROPELLER_THRUST_RATE, 0.99, 1.03 * self._weight/4.0, Propeller.ROTATION_CCW, EmulatedDrone.PROPELLER_COUNTER_ROTATION_RATE)]
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
            if EmulatedDrone.HANGED_MODE:

                for index in range(3):
                    self._state._speeds[index] += (self._state._accels[index] + previousAccels[index]) * dt2

            else:
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
                self._state._angles[2] = self._normalizeAngle(self._state._angles[2])
                
                #Calculate drone's angle-speeds
                accelAxisX = self._propellers[3].getOrtogonalAccel() - self._propellers[1].getOrtogonalAccel()
                previousAngleSpeedX = self._state._angleSpeeds[0]
                self._state._angleSpeeds[0] += accelAxisX * dt * self._arcSpeedToAngleSpeed
    
                accelAxisY = self._propellers[2].getOrtogonalAccel() - self._propellers[0].getOrtogonalAccel()
                previousAngleSpeedY = self._state._angleSpeeds[1]
                self._state._angleSpeeds[1] += accelAxisY * dt * self._arcSpeedToAngleSpeed            
    
                #Calculate drone's angles (heading was already calculated)                
                self._state._angles[0] += (self._state._angleSpeeds[0] + previousAngleSpeedX) * dt2
                self._state._angles[0] = self._normalizeAngle(self._state._angles[0])
                self._state._angles[1] += (self._state._angleSpeeds[1] + previousAngleSpeedY) * dt2
                self._state._angles[1] = self._normalizeAngle(self._state._angles[1])                                         
    
            #Update propeller angles
            for propeller in self._propellers:
                propeller.setAngles(self._state._angles)

            #if dt < 1.0:
            #    print self._state            
        
    
    def _normalizeAngle(self, angle):
        
        if angle < -180.0:
            angle +=  360.0
        elif angle > 180: 
            angle -= 360.0
            
        return angle
     
    
    def getState(self):
        
        currentState = deepcopy(self._state)
        
        if EmulatedDrone.X_CONFIGURATON:
            #Rotate angles +45º
            droneAngleX = radians(currentState._angles[0])
            droneAngleY = radians(currentState._angles[1])
            
            sinX = sin(droneAngleX)
            sinY = sin(droneAngleY)
            
            hx = (sinX + sinY)/2.0
            hy = (sinY - sinX)/2.0
            
            worldAngleX = degrees(asin(hx/EmulatedDrone.R1))
            worldAngleY = degrees(asin(hy/EmulatedDrone.R1))
            worldAngleZ = currentState._angles[2] + 45.0
            
            currentState._angles = [worldAngleX, worldAngleY, worldAngleZ]
                
        
        return currentState
        
    
    def initStateTime(self):
        
        self._state._time = time.time()
        
    
    def onPropellerUpdated(self):
        
        self._propellersUpdatedCount += 1
        if self._propellersUpdatedCount == self._propellersCount:
            
            self._updateStatus()
            self._propellersUpdatedCount = 0
            
        elif self._propellersUpdatedCount > self._propellersCount:
            
            raise Exception("Error: Any propellers updated unsuccesfully.")
        
