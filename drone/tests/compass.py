# -*- coding: utf-8 -*-

'''
Created on 18 de abr. de 2016

@author: david
'''
from sensors.pycomms.hmc5883l import HMC5883L

def main():
    
    sensor = HMC5883L()
    sensor.initialize()
    
    try:
        while True:
            data = sensor.getHeading()
            print data
    
    except KeyboardInterrupt:
        
        print "[Ctrl+C] -> stop"
        
    

if __name__ == '__main__':
    main()
