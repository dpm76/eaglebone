'''
Created on 11/04/2015

@author: david
'''

import logging
from threading import Thread
import time


class PID(object):
    '''
    Proportional Integrative Derivative stabilizer
    '''

    def __init__(self, period, kpMatrix, kiMatrix, kdMatrix, readInputDelegate, setOutputDelegate, pidName = ""):
        '''
        Constructor
        '''
        
        self._pidName = pidName
        
        length = len(kpMatrix)
        
        self._targets = [0.0] * length        
        
        #self._previousErrors = [0.0] * length #Not used currently since not using derivative component
        self._integrals = [0.0] * length
        self._lastErrors = [0.0] * length
        
        self._period = period
        self._lastTime = time.time()
        
        self._kp = kpMatrix
        self._ki = kiMatrix
        self._kd = kdMatrix
        
        self._readInput = readInputDelegate
        self._setOutput = setOutputDelegate
    
        self._isRunning = False
        self._thread = Thread(target=self._do)
        
        self._length = length
        
        self._integralsEnabled = True
        
        self._deltaTimeSum = 0.0
        self._iterationCount = 0
    
        
    def _calculate(self):
        
        outputArray = [0.0]*self._length
        
        currentValues  = self._readInput()        
        currentTime = time.time()
        dt = currentTime - self._lastTime
                
        for i in range(self._length):
            
            error = self._targets[i] - currentValues[i]
            
            if self._integralsEnabled:
                self._integrals[i] += error * dt
            else:
                self._integrals[i] = 0.0
                        
            result = \
                self._kp[i] * error \
                + self._ki[i] * self._integrals[i] \
                + (self._kd[i] * (error - self._lastErrors[i]) / dt)
            self._lastErrors[i] = error
            
            outputArray[i] = result            

        self._lastTime = currentTime
        self._setOutput(outputArray)
        
        self._deltaTimeSum += dt
        self._iterationCount += 1
    
    
    def setTarget(self, target, index):
        
        self._targets[index] = target
        
    
    def setTargets(self, targets):
        
        self._targets = targets
        
        
    def getTarget(self, index):
        
        return self._targets[index]
    
    
    def getTargets(self):
        
        return self._targets
        
    
    def _do(self): 
        
        dtSum = 0.0
        iterCount = 0
        
        self._lastTime = time.time()
        time.sleep(self._period)
        while self._isRunning:
        
            t0 = time.time()
        
            self._calculate()
            
            calculationTime = time.time() - t0
            dtSum += calculationTime
            iterCount += 1            
            
            sleepTime = self._period - calculationTime 
            if sleepTime > 0.0:            
                time.sleep(sleepTime)
            else:
                freq = 1.0/self._period
                maxFreq = 1.0/calculationTime
                message="This machine cannot operate at {0:.0f}Hz. Max @{1:.3f}Hz".format(freq, maxFreq)
                print message
                logging.error(message)
                time.sleep(0.001)

        if dtSum != 0.0 and iterCount != 0:
            tAvg = dtSum * 1000.0 / iterCount
            fAvg = float(iterCount) / dtSum
        else:
            tAvg = 0.0
            fAvg = float("inf")
            
        message = "PID-\"{0}\" (net values) t: {1:.3f}ms; f: {2:.3f}Hz".format(self._pidName, tAvg, fAvg)
        logging.info(message)
        print message
        
    
    def start(self):
        
        if not self._thread.isAlive():
            
            logging.info("Starting PID-\"{0}\"".format(self._pidName))

            self._deltaTimeSum = 0.0
            self._iterationCount = 0
            
            self._isRunning = True
            self._thread.start()
            
        
    def stop(self):
        
        self._isRunning = False        
        if self._thread.isAlive():
            
            self._thread.join()
            
            if self._iterationCount != 0 and self._deltaTimeSum:
                
                averageDeltaTime = self._deltaTimeSum * 1000.0/ self._iterationCount
                averageFrequency = self._iterationCount / self._deltaTimeSum
                
            else:
                
                averageDeltaTime = 0.0
                averageFrequency = float("inf")
                
            message = "PID-\"{0}\" - Avg. time: {1:.3f}ms - Avg. freq: {2:.3f}Hz".format(self._pidName, averageDeltaTime, averageFrequency)
            print message
            logging.info(message)
                
    
    def disableIntegrals(self):
        
        self._integralsEnabled = False
        
        
    def enableIntegrals(self):
        
        self._integralsEnabled = True
       
    