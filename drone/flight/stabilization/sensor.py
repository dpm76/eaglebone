# -*- coding: utf-8 -*-
'''
Created on 11/04/2015

@author: david
'''
from copy import deepcopy
import logging
import math
import time

from flight.stabilization.state import SensorState
import flight.stabilization.imu3000_defs as imu3000
import flight.stabilization.kxtf9_defs as kxtf9
from sensors.vector import Vector


try:
    import smbus
    
except ImportError:
    
    class smbus(object):
        @staticmethod
        def SMBus(channel):
            raise Exception("smbus module not found!")


class Sensor(object):
    '''
    Gyro and accelerometer
    '''
    
    GYRO_ADDRESS = 0x68
    ACC_ADDRESS = 0x0f

    GRAVITY = 9.807 # m/s²
    PI2 = math.pi / 2.0

    GYRO2DEG = 250.0 / 32768.0
    ACCEL2G = 2.0 / 2048.0
    ACCEL2MS2 = ACCEL2G * GRAVITY

    ACCEL_LPF = 0.4 #Acceleration low-pass filter constant

   
    def __init__(self):
        '''
        Constructor
        '''
        
        self._bus = smbus.SMBus(1)
        
        self._gyroOffset = [0]*3
        
        self._gyroReadTime = time.time()
        
        self._previousAngles = [0.0]*3
        
        self._accOffset = [0]*3

        self._accAnglesOffset = [0.0]*2
        
        self._lastReadAccRawData = [0]*3
        self._accLastFilteredRawData = [0]*3
        self._angSpeed = [0.0]*2
        self._localGravity = 0.0
        
        self._state = SensorState()
        
    
    def _readWord(self, address, regH, regL):

        byteH = self._bus.read_byte_data(address, regH)
        byteL = self._bus.read_byte_data(address, regL)
    
        word = (byteH << 8) | byteL
        if (byteH & 0x80) != 0:
            word = -(0xffff - word + 1)
    
        return word
    

    def _readWordHL(self, address, reg):
    
        return self._readWord(address, reg, reg+1)
    

    def _readWordLH(self, address, reg):

        return self._readWord(address, reg+1, reg)
    

    def _writeWord(self, address, regH, regL, word):
    
        byteH = word >> 8
        byteL = word & 0xff
    
        self._bus.write_byte_data(address, regH, byteH)
        self._bus.write_byte_data(address, regL, byteL)


    def _writeWordHL(self, address, reg, word):
    
        self._writeWord(address, reg, reg+1, word)


    def _writeWordLH(self, address, reg, word):
    
        self._writeWord(address, reg+1, reg, word)

    
    def _readRawGyroX(self):
        
        return self._readWordHL(Sensor.GYRO_ADDRESS, imu3000.GYRO_XOUT)
    
    
    def _readRawGyroY(self):
        
        return self._readWordHL(Sensor.GYRO_ADDRESS, imu3000.GYRO_YOUT)
    
    
    def _readRawGyroZ(self):
        
        return self._readWordHL(Sensor.GYRO_ADDRESS, imu3000.GYRO_ZOUT)
    
    
    def _readAngSpeed(self, reg, index):

        data = (self._readWordHL(Sensor.GYRO_ADDRESS, reg) - self._gyroOffset[index]) * Sensor.GYRO2DEG
        return data


    def readAngleSpeeds(self):
        
        return self._state.angleSpeeds
    

    def _readAngleSpeeds(self):

        speedAX = self._readAngSpeedX()
        speedAY = self._readAngSpeedY()        
        speedAZ = self._readAngSpeedZ()

        self._state.angleSpeeds = [speedAX, speedAY, speedAZ]


    def _readAngSpeedX(self):
        
        return self._readAngSpeed(imu3000.GYRO_XOUT, 0)


    def _readAngSpeedY(self):
        
        return self._readAngSpeed(imu3000.GYRO_YOUT, 1)


    def _readAngSpeedZ(self):
        
        return self._readAngSpeed(imu3000.GYRO_ZOUT, 2)


    def _readAccAngles(self):
        
        rawAccX = self._readRawAccelFilteredX()
        rawAccY = self._readRawAccelFilteredY()
        rawAccZ = self._readRawAccelFilteredZ()
        
        accAngX = math.degrees(math.atan2(rawAccY, rawAccZ))
        accAngY = -math.degrees(math.atan2(rawAccX, rawAccZ))
        
        accAngles = [accAngX, accAngY]
        
        return accAngles


    def readAngles(self):
        
        return self._state.angles
    

    def _readAngles(self):
        
        accAngles = self._readAccAngles()
        previousAngSpeeds = self._angSpeed 
        self._angSpeed = [self._state.angleSpeeds[0],self._state.angleSpeeds[1]] #[self._readAngSpeedX(), self._readAngSpeedY()]
        currentTime = time.time()
        dt2 = (currentTime - self._gyroReadTime) / 2.0        
        
        currentAngles = [0.0]*3
        
        for index in range(2):
            expectedAngle = self._previousAngles[index] + \
                (previousAngSpeeds[index] + self._angSpeed[index]) * dt2            
            currentAngles[index] = 0.2 * accAngles[index] + 0.8 * expectedAngle
        
        self._gyroReadTime = currentTime
        self._previousAngles = currentAngles
        
        self._state.angles = deepcopy(currentAngles)

   
    def readDeviceAngles(self):

        angles = self.readAngles()
        deviceAngles = [angles[0] - self._accAnglesOffset[0], angles[1] - self._accAnglesOffset[1], 0.0]

        return deviceAngles

    
    def _readRawAccelX(self):
        
        return self._readWordLH(Sensor.ACC_ADDRESS, kxtf9.XOUT) / 16
    
    
    def _readRawAccelY(self):
        
        return self._readWordLH(Sensor.ACC_ADDRESS, kxtf9.YOUT) / 16
    
    
    def _readRawAccelZ(self):
        
        return self._readWordLH(Sensor.ACC_ADDRESS, kxtf9.ZOUT) / 16


    def _readRawAccelFilteredX(self):
        
        filteredValue = self._accLastFilteredRawData[0] + \
            Sensor.ACCEL_LPF *( self._readRawAccelX() - self._accLastFilteredRawData[0])
        self._accLastFilteredRawData[0] = filteredValue

        return filteredValue
    
    
    def _readRawAccelFilteredY(self):
        
        filteredValue = self._accLastFilteredRawData[1] + \
            Sensor.ACCEL_LPF *( self._readRawAccelY() - self._accLastFilteredRawData[1])
        self._accLastFilteredRawData[1] = filteredValue
    
        return filteredValue

    
    def _readRawAccelFilteredZ(self):
        
        filteredValue = self._accLastFilteredRawData[2] + \
            Sensor.ACCEL_LPF *( self._readRawAccelZ() - self._accLastFilteredRawData[2])
        self._accLastFilteredRawData[2] = filteredValue

        return filteredValue

    
    def readAccels(self):
        
        return self._state.accels
    
    
    def _readAccels(self):

        accelX = self._readRawAccelFilteredX() * Sensor.ACCEL2MS2
        accelY = self._readRawAccelFilteredY() * Sensor.ACCEL2MS2
        accelZ = self._readRawAccelFilteredZ() * Sensor.ACCEL2MS2
        
        angles = [math.radians(angle) for angle in self.readAngles()]

        accels = Vector.rotateVector3D([accelX, accelY, accelZ], angles + [0.0])
                  
        #Eliminate gravity acceleration
        accels[2] -= self._localGravity

        self._state.accels = accels
        
    
    def resetGyroReadTime(self):
        
        self._gyroReadTime = time.time()
    
    
    def refreshState(self):
        
        self._readAngleSpeeds()
        self._readAngles()
        self._readAccels()
        
    
    def start(self):
        '''        
         Initializes sensor
        '''
        
        startMessage = "Using IMU-3000."
        print(startMessage)
        logging.info(startMessage)
        
        #Initializes gyro
        self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.PWR_MGM, imu3000.H_RESET)
        self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.PWR_MGM, imu3000.CLK_SEL_X)
        #1kHz (as DPLF_CG_5) / (SMPLRT_DIV +1) => sample rate @50Hz
        self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.SMPLRT_DIV, 19)
        #DLPF_CFG_5: Low-pass filter @5Hz; analog sample rate @1kHz
        self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.DLPF_FS, imu3000.FS_SEL_250 | imu3000.DLPF_CFG_5)
        
        # Initialize accelerometer
        self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.USER_CTRL, imu3000.AUX_IF_RST)
    
        self._bus.write_byte_data(Sensor.ACC_ADDRESS, kxtf9.CTRL_REG1, 0)
        self._bus.write_byte_data(Sensor.ACC_ADDRESS, kxtf9.CTRL_REG1, kxtf9.RES | kxtf9.GSEL_4G)
        self._bus.write_byte_data(Sensor.ACC_ADDRESS, kxtf9.CTRL_REG1, kxtf9.RES | kxtf9.GSEL_4G | kxtf9.PC1)
        
        self._accLastFilteredRawData = [self._readRawAccelX(), self._readRawAccelY(), self._readRawAccelZ()]

        #Wait to sensor's start-up
        time.sleep(1)
        
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
        
        #Calculate local gravity
        angles = [math.radians(angle) for angle in self._accAnglesOffset]
        accels = [accel * Sensor.ACCEL2MS2 for accel in self._accOffset]       
        self._localGravity = Vector.rotateVector3D(accels, angles + [0.0])[2]
            
        #TODO Calculate accel-Z error
        
    def getMaxErrorZ(self):
        
        return 0.1
    
    
    def stop(self):
        
        pass        
        
        #self._bus.write_byte_data(Sensor.ACC_ADDRESS, kxtf9.CTRL_REG1, 0)
        #self._bus.write_byte_data(Sensor.GYRO_ADDRESS, imu3000.PWR_MGM, imu3000.SLEEP)
        
