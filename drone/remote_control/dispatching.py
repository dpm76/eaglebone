# -*- coding: utf-8 -*-

'''
Created on 15/06/2015

@author: david
'''

from SocketServer import StreamRequestHandler
import json
import logging
from threading import Thread
import traceback

from config import Configuration
from flight.controller import FlightController


class Dispatcher(StreamRequestHandler):

    MAX_ANGLE = 2.0 #TODO currently angles. Replace by acceleration (m/s²) later
    MAX_ACCEL_Z = 0.5 #m/s² steps of 0.005 m/s²
    MAX_ANGLE_SPEED = 20.0 #º/s for yaw

    def setup(self):
        
        StreamRequestHandler.setup(self)
        
        self._controller = FlightController.getInstance()
        self._controller.start()
        
        self._throttleByUser = False
        self._throttle = 0.0        
        self._started = False
        
        
    def finish(self):
                
        StreamRequestHandler.finish(self)
        self._controller.stop()
    
    
    def handle(self):
        
        logMessage = "Remote control connected. Waiting for commands..."
        logging.info(logMessage)
        print logMessage

        try:
            done = False
            while not done:
                
                rawMessage = self.rfile.readline().strip()
                
                if rawMessage != "":
                    message = json.loads(rawMessage)
                    logging.debug("Received: key: '{0}'; data: {1}".format(message["key"], message["data"]))
    
                    done = message["key"] == "close"
                    if not done:
                        Thread(target=self._dispatch, args=[message]).start()
                else:
                    done = True
                    
        except Exception as ex:
            
            logging.error("Dispatching-error {0}".format(ex))   
            logging.error(traceback.format_exc())                 

        logMessage = "Connection end"
        logging.info(logMessage)
        print logMessage

  
    def _dispatch(self, message):
        
        if self._started and message["key"] == "target":
            
            controlData = message["data"]
            newTargets = [controlData[0] * Dispatcher.MAX_ANGLE / 100.0,
                          controlData[1] * Dispatcher.MAX_ANGLE / 100.0,
                          controlData[2] * Dispatcher.MAX_ANGLE_SPEED / 100.0,
                          controlData[3] * Dispatcher.MAX_ACCEL_Z / 100.0]            
            
            self._controller.setTargets(newTargets)
            
        elif self._started and message["key"] == "throttle":
            
            if not self._throttleByUser:
                #Disable Z-accel stabilization
                self._controller.alterPidAccelConstants(2, 0.0, 0.0, 0.0)
                self._throttle = 0
                self._controller.standBy()
                
                self._throttleByUser = True
            
             
            newThrottle = message["data"]
 
            if newThrottle > 0:
                dThrottle = newThrottle - self._throttle
                 
                if dThrottle != 0:
                    self._throttle = newThrottle
             
                    self._controller.addThrottle(dThrottle)
            else:
                self._throttle = 0
                self._controller.standBy()
        
        elif message["key"] == "is-started":
            
            self._started = message["data"]
            self._throttle = 0
            
            if self._started:
                self._controller.standBy()
                self._controller.startPid()
                    
            else:                
                self._controller.stopPid()
                self._controller.idle()                

#         elif message["key"] == "integrals":
#             
#             enable = message["data"]
#             
#             if enable:                
#                 self._controller.enableIntegrals()
#             else:
#                 self._controller.disableIntegrals()
                
        elif message["key"] == "pid-calibration":
            
            data = message["data"]
            
            axisSwitcher = {
                            "X": 0,
                            "Y": 1,
                            "Z": 2
                            }
            
            axisIndex = axisSwitcher.get(data["axis"])
            constantP = data["p"]
            constantI = data["i"]
            constantD = data["d"]
            
            pidLevel = data["pid"]
            
            if pidLevel == "ang-speed":            
                self._controller.alterPidAnglesSpeedConstants(axisIndex, constantP, constantI, constantD)
                
            elif pidLevel == "angles":
                self._controller.alterPidAnglesConstants(axisIndex, constantP, constantI, constantD)
                
            else: #accel
                self._controller.alterPidAccelConstants(axisIndex, constantP, constantI, constantD)
         
        elif message["key"] == "read-drone-config":

            config = Configuration.getInstance().getConfig()
            self._send(message["key"], config)
            
        elif message["key"] == "read-drone-state":
            
            state = self._controller.readState()
            self._send(message["key"], state.__dict__)

    
    def _send(self, responseKey, message):
            
            try:        
                serializedMessage = json.dumps({"key": responseKey, "response": message})                
                self.wfile.write(serializedMessage + "\n")
                
            except Exception as ex:
                logging.error("Cannot send object '{0}': {1}".format(message, ex))            
