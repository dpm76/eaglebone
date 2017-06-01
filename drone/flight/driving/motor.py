# -*- coding: utf-8 -*-

"""
Created on 06/04/2015

@author: david
"""
import logging
from os import system
from os.path import exists

from flight.driving.sysfs_writer import SysfsWriter


class Motor(object):
    """
    Controls a single motor
    """
    
    KEY_PWM_ID = "pwmId"
    KEY_PIN_ID = "pinId" 
    
    #BeagleBone's config.
    #TODO 20150408 DPM - Include this configuration in such a settings file
    _pins = [{KEY_PWM_ID: 6, KEY_PIN_ID: "P8.13"},
             {KEY_PWM_ID: 5, KEY_PIN_ID: "P8.19"},
             {KEY_PWM_ID: 4, KEY_PIN_ID: "P9.16"},
             {KEY_PWM_ID: 3, KEY_PIN_ID: "P9.14"}]
    
    PERIOD = 20000000 #nanoseconds = 50Hz
    
    MIN_DUTY = 1000000 #nanoseconds    
    MAX_DUTY = 2000000 #nanoseconds
    
    RANGE_DUTY = (MAX_DUTY - MIN_DUTY) / 100.0

    MAX_THROTTLE = 80.0 #percentage


    def __init__(self, motorId):
        """
        Constructor
        
        @param motorId: Identificator of the motor. A number between 0 to 3 (in case of quadcopter)  
        """
        
        pinIndex = motorId
        self._pwmId = Motor._pins[pinIndex][Motor.KEY_PWM_ID]
        self._pinId = Motor._pins[pinIndex][Motor.KEY_PIN_ID]
        
        self._motorId = motorId
        
        self._throttle = 0.0
        self._duty = 0
        
    
    def start(self):
        """
        Starts the motor up
        """
        
        if not exists("/sys/class/pwm/pwm{0}".format(self._pwmId)):
            system("config-pin {0} pwm".format(self._pinId))
            #SysfsWriter.writeOnce("pwm", "/sys/devices/ocp.*/{0}_pinmux.*/state".format(self._pinId))
            SysfsWriter.writeOnce(str(self._pwmId), "/sys/class/pwm/export")
        
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/duty_ns".format(self._pwmId))
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        SysfsWriter.writeOnce(str(Motor.PERIOD), "/sys/class/pwm/pwm{0}/period_ns".format(self._pwmId))
        SysfsWriter.writeOnce("1", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        
        self._sysfsWriter = SysfsWriter("/sys/class/pwm/pwm{0}/duty_ns".format(self._pwmId))
        
        logging.info("motor {0}: started".format(self._motorId))
        
        
    def setThrottle(self, throttle):
        """
        Sets the motor's throttle
        
        @param throttle: Motor power as percentage 
        """
        
        self._throttle = float(throttle)

        if self._throttle >= 0.0 and self._throttle <= Motor.MAX_THROTTLE:            
        
            self._duty = int((Motor.RANGE_DUTY * self._throttle) + Motor.MIN_DUTY)
            #logging.debug("motor {0}: duty={1}; throttle={2}".format(self._motorId, self._duty, self._throttle))
        
            self._sysfsWriter.write(str(self._duty))

        #else:
        #    logging.debug("motor {0}: duty={1}; throttle={2} (virtual)".format(self._motorId, self._duty, self._throttle))
        
    
    def getThrottle(self):
        
        return self._throttle
    
    
    def addThrottle(self, increment):
        """
        Increases or decreases the motor's throttle
        
        @param increment: Value added to the current throttle percentage. This can be negative to decrease.
        """
        
        self.setThrottle(self._throttle + increment)
        
    
    def setMaxThrottle(self):
        """
        Sends the max throttle signal (useful for calibrating process)
        """
        
        #logging.debug("motor {0}: max-throttle".format(self._motorId))
        
        self._throttle = 100.0
        self._duty = Motor.MAX_DUTY

        self._sysfsWriter.write(str(Motor.MAX_DUTY))
        
        
    def setMinThrottle(self):
        """
        Sends the min throttle signal (useful for calibrating process, or setting the motor in stand-by state)
        """
        
        #logging.debug("motor {0}: min-throttle".format(self._motorId))
        
        self._throttle = 0.0
        self._duty = Motor.MIN_DUTY
        
        self._sysfsWriter.write(str(Motor.MIN_DUTY))

        
    def standBy(self):
        """
        Set the motor in stand-by state
        """
        
        logging.info("motor {0}: stand-by".format(self._motorId))
        self.setMinThrottle()        
        
        
    def idle(self):
        """
        Set the motor in idle state
        """
        
        logging.info("motor {0}: idle".format(self._motorId))
        
        self._throttle = 0.0
        self._duty = 0
        
        self._sysfsWriter.write("0")
        
        
    def stop(self):
        """
        Stops the motor
        """
        
        logging.info("motor {0}: stop".format(self._motorId))
        
        self._throttle = 0.0
        self._duty = 0
        
        self._sysfsWriter.close()
        SysfsWriter.writeOnce("0", "/sys/class/pwm/pwm{0}/run".format(self._pwmId))
        
    
        
