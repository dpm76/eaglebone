# -*- coding: utf-8 -*-

'''
Created on 14/04/2015

@author: david
'''
import logging
import time

from config import Configuration
from emulation.drone import EmulatedDrone
from emulation.sensor import EmulatedSensor
from flight.driving.driver import Driver
from flight.stabilization.pid import PID
from flight.stabilization.sensor import Sensor
from flight.state import State
from sensors.IMU_dummy import IMUDummy
from sensors.imu3000_emu import Imu3000Emulated
from sensors.imu6050dmp import Imu6050Dmp


class FlightController(object):
    
    PID_PERIOD = 0.02  # seconds (50Hz)
    
    _instance = None
    
    @staticmethod
    def getInstance():
        
        if FlightController._instance == None:
            FlightController._instance = FlightController()
            
        return FlightController._instance
    
    
    def __init__(self):
        
        self._config = Configuration.getInstance().getConfig()
        
        self._driver = Driver()
        self._createSensor(self._config[Configuration.KEY_IMU_CLASS])
        
        #PID constants must have the same length
        self._pidAnglesSpeedKP = self._config[Configuration.PID_ANGLES_SPEED_KP] 
        self._pidAnglesSpeedKI = self._config[Configuration.PID_ANGLES_SPEED_KI]
        self._pidAnglesSpeedKD = self._config[Configuration.PID_ANGLES_SPEED_KD]
        
        #PID constants must have the same length
        self._pidAnglesKP = self._config[Configuration.PID_ANGLES_KP] 
        self._pidAnglesKI = self._config[Configuration.PID_ANGLES_KI]
        self._pidAnglesKD = self._config[Configuration.PID_ANGLES_KD]
        
        self._pidAccelKP = self._config[Configuration.PID_ACCEL_KP]
        self._pidAccelKI = self._config[Configuration.PID_ACCEL_KI]
        self._pidAccelKD = self._config[Configuration.PID_ACCEL_KD]
        
        #PID
        self._pidKP = self._pidAnglesSpeedKP + self._pidAnglesKP + self._pidAccelKP
        self._pidKI = self._pidAnglesSpeedKI + self._pidAnglesKI + self._pidAccelKI
        self._pidKD = self._pidAnglesSpeedKD + self._pidAnglesKD + self._pidAccelKD
        
        self._pid = PID(FlightController.PID_PERIOD, \
                        self._pidKP, self._pidKI, self._pidKD, \
                        self._readPIDInput, self._setPIDOutput, \
                        "stabilization-pid")
        self._pid.setTargets([0.0]*len(self._pidKP))        

        self._isRunning = False
        
        self._pidThrottleThreshold = 0
        
        
    def setPidThrottleThreshold(self, throttle):

        self._pidThrottleThreshold = throttle


    def _createSensor(self, imuClass):

        if imuClass == Configuration.VALUE_IMU_CLASS_3000:
            
            self._sensor = Sensor()
            
#         elif imuClass == Configuration.VALUE_IMU_CLASS_REMOTE:
#             
#             self._remote = rpyc.classic.connect(self._config[Configuration.KEY_REMOTE_ADDRESS])
#             imuDummy = self._remote.modules["sensors.IMU_dummy"]
#             self._sensor = imuDummy.IMUDummy()

        elif imuClass == Configuration.VALUE_IMU_CLASS_3000EMU:
            
            self._sensor = Imu3000Emulated()
            
        elif imuClass == Configuration.VALUE_IMU_CLASS_6050:
            
            self._sensor = Imu6050Dmp()
            
        elif imuClass == Configuration.VALUE_IMU_CLASS_EMULATION:
            
            self._sensor = EmulatedSensor(EmulatedDrone.REALISTIC_FLIGHT)
            
        else: #Dummy as default
            
            self._sensor = IMUDummy()
            
    
    def _readPIDAnglesSpeedInput(self):

        inputData = self._sensor.readAngleSpeeds()

        logging.debug("PID-angles-speed input: {0}".format(inputData))
        
        return inputData


    def _setPIDAnglesSpeedOutput(self, output):
        
        #angle-speed Z
        self._driver.spin(output[2])
        
        logging.debug("PID-angles-speed output: {0}".format(output))
    
    
    def _readPIDAnglesInput(self):

        angles = self._sensor.readDeviceAngles()
        
        logging.debug("PID-angles input: {0}".format(angles))

        return angles


    def _setPIDAnglesOutput(self, output):
       
        #angle X
        #Moving the drone along Y-direction makes it turning on X-axis 
        #Caution! Angle around X-axis as positive sense means moving backwards
        self._driver.shiftY(-output[0])
        
        #angle Y
        #Moving the drone along X-direction makes it turning on Y-axis
        self._driver.shiftX(output[1])
                        
        logging.debug("PID-angles output: {0}".format(output))
    
    
    def _readPIDAccelInput(self):
        
        inputData = self._sensor.readAccels()

        logging.debug("PID-accel input: {0}".format(inputData))

        return inputData
        
    
    def _setPIDAccelOutput(self, output):
        
        #accel Z
        
        self._driver.addThrottle(output[2])

        logging.debug("PID-accel output: {0}".format(output))
        

    def _readPIDInput(self):
        
        logging.debug("Targets: {0}".format(self._pid.getTargets()))
        
        self._sensor.refreshState()
        anglesSpeedInput = self._readPIDAnglesSpeedInput()
        anglesInput = self._readPIDAnglesInput()[0:2]
        accelInput = self._readPIDAccelInput()
        
        pidInput = anglesSpeedInput + anglesInput + accelInput
        
        return pidInput         
    
    
    def _setPIDOutput(self, output):
        
        anglesSpeedOutput = output[0:3]
        anglesOutput = output[3:5]
        accelOutput = output[5:8]
        
        self._setPIDAnglesSpeedOutput(anglesSpeedOutput)
        self._setPIDAnglesOutput(anglesOutput)
        self._setPIDAccelOutput(accelOutput)
        
        self._driver.commitIncrements()
        
    
    def addThrottle(self, increment):
        
        throttle0 = self._driver.getBaseThrottle()
        self._driver.addThrottle(increment)
        throttle1 = self._driver.getBaseThrottle()
        
        if throttle1 >= self._pidThrottleThreshold \
            and throttle0 < self._pidThrottleThreshold:
            
            self._startPid()
            
        elif throttle1 < self._pidThrottleThreshold \
            and throttle0 >= self._pidThrottleThreshold:
            
            self._stopPid()
            self._driver.setThrottle(throttle1)
        
        if not self._pid.isRunning():
            
            self._driver.commitIncrements()
        

    def setTargets(self, targets):
        
        self._pid.setTarget(targets[0], 3) #angle X
        self._pid.setTarget(targets[1], 4) #angle Y
        self._pid.setTarget(targets[2], 2) #angle speed Z
        self._pid.setTarget(targets[3], 7) #accel Z
        
     
#     def enableIntegrals(self):
# 
#         self._pid.enableIntegrals()
#         
#         
#     def disableIntegrals(self):
# 
#         self._pid.disableIntegrals()
#                

    def start(self):
        
        if not self._isRunning:
        
            self._isRunning = True
            
            self._sensor.start()        
            self._driver.start()
            self._driver.idle()        
    
        
    def _startPid(self):

        if self._isRunning:

            print("Starting PID...")
            logging.info("Starting PID...")

            self._sensor.resetGyroReadTime()
            
            time.sleep(FlightController.PID_PERIOD)            
            self._sensor.refreshState()
            
            self._pid.start()
            
    
    def _stopPid(self):
        
        self._pid.stop()
        
        print("PID finished.")
        logging.info("PID finished.")
                
    
    def stop(self):
        
        if self._isRunning:
        
            self._isRunning = False
            
            self._stopPid()               
            self.idle()
            
            self._driver.stop()        
            self._sensor.stop()
        
        
    def standBy(self):
        
        self._stopPid()
        self._driver.standBy()
    

    def idle(self):
        
        self._stopPid()
        self._driver.idle()
        
    
    def alterPidAnglesSpeedConstants(self, axisIndex, valueP, valueI, valueD):
        
        if axisIndex < len(self._pidAnglesSpeedKP):
            
            self._pidKP[axisIndex] = valueP
            self._pidKI[axisIndex] = valueI
            self._pidKD[axisIndex] = valueD
        

    def alterPidAnglesConstants(self, axisIndex, valueP, valueI, valueD):
        
        if axisIndex < len(self._pidAnglesKP):

            axisIndex += 3
                        
            self._pidKP[axisIndex] = valueP
            self._pidKI[axisIndex] = valueI
            self._pidKD[axisIndex] = valueD
            
            print("constantes: {0}".format([valueP, valueI, valueD]))
            

    def alterPidAccelConstants(self, axisIndex, valueP, valueI, valueD):
        
        if axisIndex < len(self._pidAccelKP):
            
            axisIndex += 5
            
            self._pidKP[axisIndex] = valueP
            self._pidKI[axisIndex] = valueI
            self._pidKD[axisIndex] = valueD


    def isRunning(self):
        
        return self._isRunning


    def readState(self):
        
        state = State()
        
        state._throttles = self._driver.getThrottles()
        state._angles = self._sensor.readDeviceAngles()
        state._angles[2] = self._sensor.readAngleSpeeds()[2]
        state._accels = self._sensor.readAccels()
        state._currentPeriod = self._pid.getCurrentPeriod()
        
        return state
    