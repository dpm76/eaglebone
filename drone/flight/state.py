# -*- coding: utf-8 -*-
'''
Created on 22 de feb. de 2016

@author: david
'''

class State(object):
    '''
    Drone's state as sensor notices
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        _throttles = [0.0]*4
        _angles = [0.0]*3
        _accels = [0.0]*3
        _speeds = [0.0]*3
        _height = 0.0
        _currentPeriod = 0.0
        