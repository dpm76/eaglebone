# -*- coding: utf-8 -*-
'''
Created on 28/01/2016

@author: david
'''
import json
import logging
import math
from os import path
import time

from sensors.vector import Vector


class Imu3000Emulated(object):
    '''
    IMU 3000 + KXTF9 emulated
    '''

    ACCEL_LPF = 0.1 #Acceleration low-pass filter
    PI2 = math.pi / 2.0
    GRAVITY = 9.807 # m/s²
    GYRO2DEG = 250.0 / 32768.0
    ACCEL2G = 2.0 / 2048.0
    ACCEL2MS2 = ACCEL2G * GRAVITY

    #CALIBRATION_FILE_PATH = "../calibration.config.json"
   
   
    def __init__(self):
        '''
        Constructor
        '''
        
        self._gyroOffset = [0]*3
        
        self._gyroReadTime = time.time()
        
        self._previousAngles = [0.0]*3
        
        self._accOffset = [0]*3

        self._accAnglesOffset = [0.0]*2
        
        self._lastReadAccRawData = [0]*3
        self._accLastFilteredRawData = [0]*3

    
    def _readRawGyroX(self):

        return 0
    
    
    def _readRawGyroY(self):

        return 0
    
    
    def _readRawGyroZ(self):

        return 0
    
    
    def _readAngSpeed(self, readRawGyroDelegate, index):

        data = (readRawGyroDelegate() - self._gyroOffset[index]) * Imu3000Emulated.GYRO2DEG

        return data


    def readAngleSpeeds(self):

        speedAX = self._readAngSpeedX()
        speedAY = self._readAngSpeedY()        
        speedAZ = self._readAngSpeedZ()

        time.sleep(0.001)

        return [speedAX, speedAY, speedAZ]


    def _readAngSpeedX(self):
        
        return self._readAngSpeed(self._readRawGyroX, 0)


    def _readAngSpeedY(self):
        
        return self._readAngSpeed(self._readRawGyroY, 1)


    def _readAngSpeedZ(self):
        
        return self._readAngSpeed(self._readRawGyroZ, 2)


    def _readAccAngles(self):

        rawAccX = self._readRawAccelFilteredX()
        rawAccY = self._readRawAccelFilteredY()
        rawAccZ = self._readRawAccelFilteredZ()
        
        accAngX = math.degrees(math.atan2(rawAccY, rawAccZ))
        accAngY = -math.degrees(math.atan2(rawAccX, rawAccZ))
        
        accAngles = [accAngX, accAngY]
        
        return accAngles


    def readAngles(self):
        
        accAngles = self._readAccAngles()        
        angSpeed = [self._readAngSpeedX(), self._readAngSpeedY()]
        currentTime = time.time()
        dt = currentTime - self._gyroReadTime
        
        currentAngles = [0.0]*3
        
        for index in range(2):
            expectedAngle = self._previousAngles[index] + angSpeed[index] * dt
            currentAngles[index] = 0.7 * accAngles[index] + 0.3 * expectedAngle
        
        self._gyroReadTime = currentTime
        self._previousAngles = currentAngles
        
        return currentAngles        


    def readDeviceAngles(self):

        angles = self.readAngles()

        angles[0] -= self._accAnglesOffset[0]
        angles[1] -= self._accAnglesOffset[2]

        return angles

    
    def _readRawAccelX(self):
        
        return 0
    
    
    def _readRawAccelY(self):
        
        return 0
    
    
    def _readRawAccelZ(self):
        
        return 0


    def _readRawAccelFilteredX(self):
        
        filteredValue = self._accLastFilteredRawData[0] + \
            Imu3000Emulated.ACCEL_LPF *( self._readRawAccelX() - self._accLastFilteredRawData[0])
        self._accLastFilteredRawData[0] = filteredValue

        return filteredValue
    
    
    def _readRawAccelFilteredY(self):
        
        filteredValue = self._accLastFilteredRawData[1] + \
            Imu3000Emulated.ACCEL_LPF *( self._readRawAccelY() - self._accLastFilteredRawData[1])
        self._accLastFilteredRawData[1] = filteredValue
    
        return filteredValue

    
    def _readRawAccelFilteredZ(self):
        
        filteredValue = self._accLastFilteredRawData[2] + \
            Imu3000Emulated.ACCEL_LPF *( self._readRawAccelZ() - self._accLastFilteredRawData[2])
        self._accLastFilteredRawData[2] = filteredValue

        return filteredValue


    def readAccels(self):

        accelX = self._readRawAccelFilteredX() * Imu3000Emulated.ACCEL2MS2
        accelY = self._readRawAccelFilteredY() * Imu3000Emulated.ACCEL2MS2
        accelZ = self._readRawAccelFilteredZ() * Imu3000Emulated.ACCEL2MS2

        #TODO Avoid multiple angle reading within PID loop
        angles = [math.radians(angle) for angle in self.readAngles()]

        anglesX = [angles[0], Imu3000Emulated.PI2 + angles[1]]
        anglesY = [angles[0] - Imu3000Emulated.PI2, angles[1]]
        anglesZ = angles

        descX = Vector._descomposeVector(accelX, anglesX)
        descY = Vector._descomposeVector(accelY, anglesY)
        descZ = Vector._descomposeVector(accelZ, anglesZ)

        accels = [descX[0] + descY[0] + descZ[0], \
                  descX[1] + descY[1] + descZ[1], \
                  descX[2] + descY[2] + descZ[2]]

        return accels
        
    
    def resetGyroReadTime(self):
        
        self._gyroReadTime = time.time()
    
    def refreshState(self):
        pass
    
    def start(self):
        '''        
         Initializes sensor
        '''
        
        #Initializes gyro
        text = "Using emulated IMU-3000."
        print(text)
        logging.info(text)
        
        self._accLastFilteredRawData = [self._readRawAccelX(), self._readRawAccelY(), self._readRawAccelZ()]
        
        self.calibrate()
    

    def calibrate(self):
        '''
        Calibrates sensor
        '''
        
        print("Calibrating accelerometer...")
        self._accOffset = [0.0]*3
        
        i = 0
        while i < 100:

            self._accOffset[0] += self._readRawAccelX()
            self._accOffset[1] += self._readRawAccelY()
            self._accOffset[2] += self._readRawAccelZ()
            
            time.sleep(0.01)
            i+=1
        
        for index in range(3): 
            self._accOffset[index] /= float(i)
        
        
        #Calibrate gyro
        print("Calibrating gyro...")
        self._gyroOffset = [0.0]*3
        
        i = 0
        while i < 100:
            
            self._gyroOffset[0] += self._readRawGyroX()
            self._gyroOffset[1] += self._readRawGyroY()
            self._gyroOffset[2] += self._readRawGyroZ()
            
            time.sleep(0.01)
            i += 1
            
        for index in range(3):
            self._gyroOffset[index] /= float(i) 
            
        
        #Calculate sensor installation angles
        self._accAnglesOffset[0] = self._previousAngles[0] = math.degrees(math.atan2(self._accOffset[1], self._accOffset[2]))
        self._accAnglesOffset[1] = self._previousAngles[1] = -math.degrees(math.atan2(self._accOffset[0], self._accOffset[2]))
            
        #self._writeCalibrationFile()
            
        #logging.info("Sensor installed with angles: {0}".format(self._accAnglesOffset))
                
    
    def stop(self):
        
        pass
        
        
