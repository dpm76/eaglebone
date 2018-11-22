# -*- coding: utf-8 -*-

'''
Created on 14/04/2016

@author: david
'''

import unittest
from emulation.motor import EmulatedMotor

class EmulatedMotorTestCase(unittest.TestCase):

    def setUp(self):
        
        self._motor = EmulatedMotor(0)


    def test_standBy(self):

        self._motor.standBy()
        throttle = self._motor.getThrottle()

        self.assertEquals(throttle, 0, "Motor is not in stand-by state")


    def test_idle(self):

        self._motor.idle()
        throttle = self._motor.getThrottle()

        self.assertEquals(throttle, 0, "Motor is not in idle state")


    def test_stop(self):

        self._motor.stop()
        throttle = self._motor.getThrottle()

        self.assertEquals(throttle, 0, "Motor was not stopped properly")


    def test_start(self):
        
        self._motor.start()
        throttle = self._motor.getThrottle()

        self.assertEquals(throttle, 0, "Motor was not properly started")


    def test_setThrottle(self):

        throttle = EmulatedMotor.MAX_THROTTLE / 2.0
        self._motor.setThrottle(throttle)
        currentThrottle = self._motor.getThrottle()
        propellerThrottle = self._motor.getPropellerThrottle()

        self.assertEquals(currentThrottle, throttle, "Motor throttle was not properly set")
        self.assertEquals(propellerThrottle, throttle, "Motor's propeller throttle was not properly set")


    def test_setThrottle_overload(self):

        throttle = EmulatedMotor.MAX_THROTTLE + 10.0
        self._motor.setThrottle(throttle)
        currentThrottle = self._motor.getThrottle()
        propellerThrottle = self._motor.getPropellerThrottle()

        self.assertEquals(currentThrottle, throttle, "Motor throttle was not properly set")
        self.assertEquals(propellerThrottle, EmulatedMotor.MAX_THROTTLE, "Motor's propeller throttle was not properly set")


    def test_setThrottle_underload(self):

        throttle = -10.0
        self._motor.setThrottle(throttle)
        currentThrottle = self._motor.getThrottle()
        propellerThrottle = self._motor.getPropellerThrottle()

        self.assertEquals(currentThrottle, throttle, "Motor throttle was not properly set")
        self.assertEquals(propellerThrottle, 0.0, "Motor's propeller throttle was not properly set")

    
    def test_getThrottle(self):

        throttle = 20.0
        self._motor.setThrottle(throttle)

        currentThrottle = self._motor.getThrottle()
        self.assertEquals(currentThrottle, throttle, "Motor throttle was not properly read")


    def test_addThrottle_positive(self):

        self._motor.setThrottle(20.0)
        self._motor.addThrottle(5.0)

        currentThrottle = self._motor.getThrottle()

        self.assertEquals(currentThrottle, 25.0, "Motor throttle was not properly added")


    def test_addThrottle_negative(self):

        self._motor.setThrottle(20.0)
        self._motor.addThrottle(-5.0)

        currentThrottle = self._motor.getThrottle()

        self.assertEquals(currentThrottle, 15.0, "Motor throttle was not properly added")


    def test_setMaxThrottle(self):

        self._motor.setMaxThrottle()

        currentThrottle = self._motor.getThrottle()

        self.assertEquals(currentThrottle, EmulatedMotor.MAX_THROTTLE, "Motor throttle was not properly changed")


    def test_setMinThrottle(self):

        self._motor.setMinThrottle()

        currentThrottle = self._motor.getThrottle()

        self.assertEquals(currentThrottle, 0.0, "Motor throttle was not properly changed")
