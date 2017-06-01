# -*- coding: utf-8 -*-

'''
Created on 27/04/2016

@author: david
'''

import unittest
from flight.driving.driver import Driver
from config import Configuration

class DriverTestCase(unittest.TestCase):

    def setUp(self):
        
        self._driver = Driver(Configuration.VALUE_MOTOR_CLASS_EMULATION)


    def test_start(self):

        self._driver.start()
        throttles = self._driver.getThrottles()

        self.assertListEqual(throttles, [0.0]*4, "Driver was not properly started")


    def test_standBy(self):

        self._driver.standBy()
        throttles = self._driver.getThrottles()

        self.assertListEqual(throttles, [0.0]*4, "Driver is not in stand-by mode")


    def test_idle(self):

        self._driver.idle()
        throttles = self._driver.getThrottles()

        self.assertListEqual(throttles, [0.0]*4, "Driver is not in idle mode")


    def test_stop(self):

        self._driver.stop()
        throttles = self._driver.getThrottles()

        self.assertListEqual(throttles, [0.0]*4, "Driver was not properly stopped")


    def test_addThrottle(self):

        self._driver.start()
        self._driver.addThrottle(10.0)
        self._driver.commitIncrements()

        throttles = self._driver.getThrottles()

        self.assertListEqual(throttles, [10.0]*4, "Driver's motors were not properly incremented")


    def test_shiftX(self):

        self._driver.start()
        self._driver.addThrottle(50.0)
        self._driver.shiftX(10.0)
        self._driver.commitIncrements()

        throttles = self._driver.getThrottles()

        #Testing in +-configuration. X-configuration, will issue different result.
        self.assertListEqual(throttles, [40.0, 50.0, 60.0, 50.0], "Driver's motors were not properly shifted")


    def test_shiftY(self):

        self._driver.start()
        self._driver.addThrottle(50.0)
        self._driver.shiftY(10.0)
        self._driver.commitIncrements()

        throttles = self._driver.getThrottles()

        #Testing in +-configuration. X-configuration, will issue different result.
        self.assertListEqual(throttles, [50.0, 60.0, 50.0, 40.0], "Driver's motors were not properly shifted")


    def test_spin(self):

        self._driver.start()
        self._driver.addThrottle(50.0)
        self._driver.spin(10.0)
        self._driver.commitIncrements()

        throttles = self._driver.getThrottles()

        #Testing in +-configuration. X-configuration, will issue different result.
        self.assertListEqual(throttles, [60.0, 40.0, 60.0, 40.0], "Driver's motors were not properly spinned")