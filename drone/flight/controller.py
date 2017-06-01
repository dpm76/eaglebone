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
    
    PID_PERIOD = 0.006 #166.666Hz #0.02  # seconds (50Hz)
    ANGLE_SPEED_FACTOR = 1000.0 # Angle-speed's PID-constants are divided by this factor
    
    FLIGHT_MODE_ANGLE_SPEED = 0
    FLIGHT_MODE_ANGLE = 1
    FLIGHT_MODE_ACCEL = 2
    
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
        self._pidAnglesSpeedKP = [k / FlightController.ANGLE_SPEED_FACTOR for k \
                                     in self._config[Configuration.PID_ANGLES_SPEED_KP]]
        self._pidAnglesSpeedKI = [k / FlightController.ANGLE_SPEED_FACTOR for k \
                                     in self._config[Configuration.PID_ANGLES_SPEED_KI]]
        self._pidAnglesSpeedKD = [k / FlightController.ANGLE_SPEED_FACTOR for k \
                                     in self._config[Configuration.PID_ANGLES_SPEED_KD]]
        
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
        
        self._maxAngleX = self._config[Configuration.KEY_MAX_ANGLE_X]
        self._maxAngleY = self._config[Configuration.KEY_MAX_ANGLE_Y]
        #TODO: Rate mode
        #self._maxAngleSpeedX = self._config[Configuration.KEY_MAX_ANGLE_SPEED_X] #used for rate mode when implemented
        #self._maxAngleSpeedY = self._config[Configuration.KEY_MAX_ANGLE_SPEED_Y] #used for rate mode when implemented
        self._maxAngleSpeedZ = self._config[Configuration.KEY_MAX_ANGLE_SPEED_Z]
        
        #TODO: Read initial flight mode from configuration
        self._flightMode = FlightController.FLIGHT_MODE_ANGLE
        
        
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
        
        #angle X
        #Moving the drone along Y-direction makes it turning on X-axis 
        #Caution! Angle around X-axis as positive sense means moving backwards
        self._driver.shiftY(-output[0])
        
        #angle Y
        #Moving the drone along X-direction makes it turning on Y-axis
        self._driver.shiftX(output[1])
        
        #angle-speed Z
        self._driver.spin(output[2])
        
        logging.debug("PID-angles-speed output: {0}".format(output))
    
    
    def _readPIDAnglesInput(self):

        angles = self._sensor.readDeviceAngles()
        
        logging.debug("PID-angles input: {0}".format(angles))

        return angles


    def _setPIDAnglesOutput(self, output):
       
        if self._flightMode == FlightController.FLIGHT_MODE_ANGLE:
            self._pid.setTarget(output[0], 0) #angle-speed X
            self._pid.setTarget(output[1], 1) #angle-speed Y
                        
            logging.debug("PID-angles output: {0}".format(output))
    
    
    def _readPIDAccelInput(self):
        
        inputData = self._sensor.readAccels()

        logging.debug("PID-accel input: {0}".format(inputData))

        return inputData
        
    
    def _setPIDAccelOutput(self, output):
        
        #TODO: Implement accel stabilization
        
        #accel Z
        
        #self._driver.addThrottle(output[2])

        #logging.debug("PID-accel output: {0}".format(output))
        pass
        

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
            #TODO: Stop integrals only
            self._startPid()
            
        elif throttle1 < self._pidThrottleThreshold \
            and throttle0 >= self._pidThrottleThreshold:
            
            #TODO: Reset and restore integrals here
            self._stopPid()
            self._driver.setThrottle(throttle1)
        
        if not self._pid.isRunning():
            
            self._driver.commitIncrements()
        

    def setInputs(self, inputs):
        '''
        Sets the controller inputs. They will be translated into the proper 
        targets depending of the current flight mode.
        
        Input range is [-100..100]
        
        The order within the inputs-array is as follows:
        
        inputs[0]: roll 
        inputs[1]: pitch
        inputs[2]: rudder
        TODO: inputs[3]: throttle (Not implemented)        
        '''

        targets = [inputs[0] * self._maxAngleX / 100.0,
                   inputs[1] * self._maxAngleY / 100.0,
                   inputs[2] * self._maxAngleSpeedZ / 100.0]
        #inputs[3] * Dispatcher.MAX_ACCEL_Z / 100.0]


        self._pid.setTarget(targets[0], 3) #angle X
        self._pid.setTarget(targets[1], 4) #angle Y
        self._pid.setTarget(targets[2], 2) #angle speed Z
        #self._pid.setTarget(targets[3], 7) #accel Z


    
    def setTargets(self, targets):
        '''
        Set the target angles and angle-speeds directly.
        @deprecated: Beacuse safety reasons, don't use this method. Please use setInputs instead.
        '''
        
        if self._flightMode == FlightController.FLIGHT_MODE_ANGLE:
            self._pid.setTarget(targets[0], 3) #angle X
            self._pid.setTarget(targets[1], 4) #angle Y
        elif self._flightMode == FlightController.FLIGHT_MODE_ANGLE_SPEED:
            self._pid.setTarget(targets[0], 0) #angle-speed X
            self._pid.setTarget(targets[1], 1) #angle-speed Y
        else: #TODO: FlightController.FLIGHT_MODE_ACCEL
            raise Exception("Flight mode accel not implemented!")
        
        self._pid.setTarget(targets[2], 2) #angle speed Z
        self._pid.setTarget(targets[3], 7) #accel Z
        
        
    def setFlightMode(self, flightMode):
    
        self._flightMode = flightMode
        self._pid.setTargets([0.0]*len(self._pidKP))
        
     
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
            
            self._pidKP[axisIndex] = valueP / FlightController.ANGLE_SPEED_FACTOR
            self._pidKI[axisIndex] = valueI / FlightController.ANGLE_SPEED_FACTOR
            self._pidKD[axisIndex] = valueD / FlightController.ANGLE_SPEED_FACTOR
        

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
    