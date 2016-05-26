'''
Created on 22 de may. de 2016

@author: david
'''
from event import EventHook


class Joystick(object):
    '''
    Throws events depending the user behavior
    '''

    def __init__(self, name, index, numAxes, numButtons, numHats):
    
        self._name = name #Name of the product
        self._index = index #Pygame's device index
        
        self._axes = [0.0]*numAxes
        self._buttons = [0]*numButtons
        self._hats = [0.0]*numHats
        
        #Events
        self.onChanged = EventHook()
        
        self.onAxisChanged = EventHook()
        
        self.onButtonChanged = EventHook()
        self.onButtonPressed = EventHook()
        self.onButtonReleased = EventHook()
        
        self.onHatChanged = EventHook()
        self.onHatPressedNegative = EventHook()
        self.onHatPressedPositive = EventHook()
        self.onHatReleased = EventHook()

        
    def getName(self):
        
        return self._name
    
    
    def getIndex(self):
        
        return self._index
    
    
    def _setAxisValue(self, index, value):
        
        self._axes[index] = value
        
        self.onChanged.fire(self)
        self.onAxisChanged.fire(self, index)
        
    
    def axesCount(self):
        
        return len(self._axes)
    
    
    def getAllAxisValues(self):
        
        return [value * 100.0 for value in self._axes]
    
    
    def getAxisValue(self, index):
        
        return self._axes[index] * 100.0
    
    
    def _setButtonValue(self, index, value):
        
        self._buttons[index] = value
        
        self.onChanged.fire(self)
        self.onButtonChanged.fire(self, index)
        if self.isButtonPressed(index):
            self.onButtonPressed.fire(self, index)
        else:
            self.onButtonReleased.fire(self, index)
        
    
    def buttonsCount(self):
        
        return len(self._buttons)
    
    
    def getAllButtonValues(self):
        
        return [value != 0 for value in self._buttons]
    
    
    def isButtonPressed(self, index):
        
        return self._buttons[index] != 0
    
    
    def _setHatValue(self, index, value):
        
        self._hats[index] = value
        
        self.onChanged.fire(self)
        self.onHatChanged.fire(self, index)
        if self._hats[index] < 0:
            self.onHatPressedNegative.fire(self, index)
        elif self._hats[index] > 0:
            self.onHatPressedPositive.fire(self, index)
        else:
            self.onHatReleased.fire(self, index)
        
    
    def hatsCount(self):
        
        return len(self._hats)
    
    
    def getAllHatValues(self):
        
        return self._hats
    
    
    def getHatValue(self, index):
        
        return self._hats[index]
        
