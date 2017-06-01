'''
Created on 15/09/2015

@author: david
'''
import json
import socket

from threading import Thread

class INetLink(object):
    '''
    Link using a TCP/IP socket
    '''

    TIME_OUT = 3.0

    def __init__(self, ipAddress, port):
        '''
        Constructor
        '''
        
        self._ipAddress = ipAddress
        self._port = port
        
        self._link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self._callbacks = {}
        
    
    def open(self):
        
        self._link.settimeout(INetLink.TIME_OUT)
        self._link.connect((self._ipAddress, self._port))
        
    
    def send(self, message, callback=None):
        '''
        Send a message object as a dictionary.
        If response is expected, a callback method can be passed. 
        The prototype of the callback is callback(message)
        The callback's message can be None
        '''
        
        serializedMessage = json.dumps(message)
        self._link.sendall((serializedMessage + "\n").encode("utf-8"))

        if callback!=None:
            self._callbacks[message["key"]] = callback
            if len(self._callbacks) == 1:
                Thread(target=self._receive).start()
    

    def _receive(self):
        '''
        Receive a response from server.
        If timeout occurs the callback method will be invoked anyway, 
        but with message = None
        '''
        
        while len(self._callbacks) != 0:
            self._link.settimeout(INetLink.TIME_OUT)
            serializedMessage = None
            message = None
            try:
                linkFile = self._link.makefile()
                serializedMessage = linkFile.readline().strip()
                message = json.loads(serializedMessage)
                responseKey = message["key"]
                if responseKey in self._callbacks:
                    callback = self._callbacks.pop(responseKey)                            
                    callback(message["response"])                
            except Exception as ex:            
                print("Cannot read message '{0}'".format(serializedMessage))
                print("Exception: {0}".format(ex))
                
    
    def close(self):
        
        self._link.close()

    