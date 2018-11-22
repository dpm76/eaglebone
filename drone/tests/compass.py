# -*- coding: utf-8 -*-

'''
Created on 18 de abr. de 2016

@author: david
'''
from sensors.pycomms.hmc5883l import HMC5883L
from math import sqrt, atan2, degrees, asin
import time

def getSpheric(mag):

    mod = sqrt(mag['x']*mag['x'] + mag['y']*mag['y'] + mag['z']*mag['z'])
    
    '''
    if mag['y'] > 0.0:        
        theta = 90.0 - degrees(atan(float(mag['x'])/ float(mag['y'])))
    elif mag['y'] < 0.0:
        theta = 270.0 - degrees(atan(float(mag['x'])/ float(mag['y'])))
    elif mag['x'] < 0.0:
        theta = 180.0
    else:
        theta = 0.0
    '''
    theta = degrees(atan2(mag['y'], mag['x']))
    phi = degrees(asin(float(mag['z'])/float(mod)))
    
    return [mod, theta, phi]
    

def main():
    
    sensor = HMC5883L()
    sensor.initialize()
    
    try:
        while True:
            data = sensor.getHeading()
            spher = getSpheric(data)
            
            print data, ["{0:.3f}".format(val) for val in spher]
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        
        print "[Ctrl+C] -> stop"
        
    

if __name__ == '__main__':
    main()
