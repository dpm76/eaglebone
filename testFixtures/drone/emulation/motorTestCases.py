# -*- coding: utf-8 -*-

'''
Created on 14/04/2016

@author: david
'''

import unittest
from emulation.motor import EmulatedMotor

class EmulatedMotorTestFixtures(unittest.TestCase):

    def test_standBy(self):

        motor = EmulatedMotor(0)
        motor.standBy()

        throttle = motor.getThrottle()

        self.assertEquals(throttle, 0, "Motor is not in stand-by state")

