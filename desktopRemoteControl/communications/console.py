'''
Created on 15/09/2015

@author: david
'''
import time
from threading import Thread

class ConsoleLink(object):
    '''
    Emulates a link showing the output trough the console
    '''

    def __init__(self):
        
        self._emulatedProcessingTime = 3

    
    def setEmulatedProcessingTime(self, time):

        self._emulatedProcessingTime = time


    def getEmulatedProcessingTime(self):

        return self._emulatedProcessingTime


    def open(self):
        
        print("ConsoleLink open.")
        
    
    def send(self, message, callback=None):

        print(str(message))
        if callback != None:
            Thread(target=self._receive, kwargs=dict(callback=callback)).start()

    
    def _receive(self, callback):

        time.sleep(self._emulatedProcessingTime)
        callback(None)


    def close(self):
        
        print("ConsoleLink closed.")

    