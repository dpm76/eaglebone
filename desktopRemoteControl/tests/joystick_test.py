'''
Created on 19 de may. de 2016

@author: david
'''
import pygame
from time import sleep

from device.manager import JoystickManager


class Client(object):
    
    def __init__(self):
        
        self._joystickManager = JoystickManager.getInstance()        
        self._joystickManager.onStart += self._onJoystickManagerStart
                
        self._done = False
        
        self._joystick = None
        
 
    def _onJoystickChange(self, sender, data):
        
        if data.type != pygame.K_ESCAPE:
        
            print data
            
        else:
            
            self._joystickManager.stop()
            
            
    def _onJoystickManagerStart(self, sender):
        
        joysticks = self._joystickManager.getJoysticks()
        if len(joysticks) != 0:
            self._joystick = joysticks[0]
            self._joystick.onAxisChanged += self._onJoystickAxisChanged 
        
        else:            
            self._done = True
            

    def _onJoystickAxisChanged(self, sender, index):
        
        axisValue = self._joystick.getAxisValue(index)
        print "\t\t\tEje-{0}: {1}".format(index, axisValue)
        

    def do(self):
        
        self._joystickManager.start()
        
        try:
            while not self._done:
                sleep(0.1)
        
        finally:
            self._joystickManager.stop()

def main():

    client = Client()
    client.do()


if __name__ == '__main__':
    
    main()
