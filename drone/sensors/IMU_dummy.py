'''
Created on 19 de ene. de 2016

@author: david
'''
import time
import logging


class IMUDummy(object):
    '''
    Emulates an IMU sensor
    '''
    
    def __init__(self):
        pass
    
    def readAngleSpeeds(self):

        time.sleep(0.005)

        return [0.0] * 3


    def _readAngSpeedX(self):
                
        time.sleep(0.001)        
        
        return 0.0

    
    def _readAngSpeedY(self):
                
        time.sleep(0.001)
        
        return 0.0

    
    def _readAngSpeedZ(self):
                
        time.sleep(0.001)
        
        return 0.0

    
    def readAngles(self):
        
        time.sleep(0.001)
        
        return [0.0] * 3


    def readDeviceAngles(self):
        
        time.sleep(0.001)
        
        return [0.0] * 3

    
    def readAccels(self):
        
        return [0.0]*3

    
    def resetGyroReadTime(self):
        '''
        Nothing to do as dummy
        '''
        pass

    def refreshState(self):
        pass
    
    
    def start(self):

        text = "Using dummy IMU." 

        print(text)
        logging.info(text)
    
    def calibrate(self):
        pass
    

    def getMaxErrorZ(self):

        return 0.0


    def stop(self):
        pass
    