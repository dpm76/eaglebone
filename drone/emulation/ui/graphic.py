# -*- coding: utf-8 -*-
'''
Created on 25 de feb. de 2016

@author: david
'''
from Tkconstants import BOTH
from Tkinter import Tk, Frame as tkFrame, Canvas
from math import cos, sin, radians
from threading import Thread
from ttk import Frame as ttkFrame, Style

from sensors.vector import Vector


class Display(ttkFrame):
    '''
    Displays the drone state on a graphical interface
    '''

    REFRESH_PERIOD = 0.2
    
    ARM_LENGTH = 23 #pixels
    PIXELS_METER = 100.0 #pixels/meter

    _instance = None
    
    @staticmethod
    def getInstance():
        
        if Display._instance == None:
            root = Tk()
            root.geometry()
            Display._instance = Display(root)
            
        return Display._instance
    
        
    def __init__(self, parent):
        '''
        Constructor
        '''
        ttkFrame.__init__(self, parent)
        
        self._refreshTime = Display.REFRESH_PERIOD
        
        self._stateProvider = None
        self._launcherMethod = None
        
        self._isRunning = False        
        self._droneThread = None
        
        self._parent = parent
        self._initUI()
        
     
    def setStateProvider(self, stateProvider):
        
        self._stateProvider = stateProvider
        
        return self
    
    
    def setLauncherMethod(self, launcherMethod):
        
        self._launcherMethod = launcherMethod
        
        return self
       
    
    def setRefreshTime(self, refreshTime):
        
        self._refreshTime = refreshTime
        
        return self
    
    
    def start(self):
        
        if self._launcherMethod and not self._droneThread:
            self._droneThread = Thread(target=self._launcherMethod)
            self._droneThread.start()
            
        self._isRunning = True
        if self._stateProvider:
            self._refresh()
            
        self._parent.mainloop()
        
        
    def stop(self):
        
        self._isRunning = False
        if self._droneThread and self._droneThread.isAlive():
            self._droneThread.join(5.0)
            
    
    def quit(self):
        
        self.stop()
        ttkFrame.quit(self)
        
        
    def _initUI(self):
        
        self._parent.title("Drone Flight Emulator")
        self.style = Style()
        self.style.theme_use("default")
        
        self.pack(fill=BOTH, expand=1)
        
        drawFrame = tkFrame(self)
        drawFrame.grid(column=0, row=0, sticky="W")
        
        self._canvasYZ = Canvas(drawFrame, bg="white", height=200, width=200)
        self._canvasYZ.grid(column=0, row=0, sticky="W", padx=(2,0), pady=(2,0))
        
        self._canvasXZ = Canvas(drawFrame, bg="white", height=200, width=200)
        self._canvasXZ.grid(column=1, row=0, sticky="E", padx=(2,2), pady=(2,0))
        
        self._canvasXY = Canvas(drawFrame, bg="white", height=200, width=400)
        self._canvasXY.grid(column=0, row=1, columnspan=2, sticky="S", padx=(2,2), pady=(0,2))
        self._linesXY = [self._canvasXY.create_line(200,100, 200, 90, fill="#ff0000"), \
                         self._canvasXY.create_line(200,100, 210, 100, fill="#0000ff"), \
                         self._canvasXY.create_line(200,100, 200, 110, fill="#0000ff"), \
                         self._canvasXY.create_line(200,100, 190, 100, fill="#0000ff")]
        
        self._linesYZ = [self._canvasYZ.create_line(100,200, 90, 200, fill="#0000ff"), \
                         self._canvasYZ.create_line(100,200, 110, 200, fill="#0000ff")]
        
        self._linesXZ = [self._canvasXZ.create_line(100,200, 90, 200, fill="#0000ff"), \
                         self._canvasXZ.create_line(100,200, 110, 200, fill="#0000ff")]
        
            
    def _plotXY(self, coord, angles):

        x = int((coord[0]*Display.PIXELS_METER + 200.0) % 400.0)
        y = int((100.0 - coord[1]*Display.PIXELS_METER) % 200.0)
        
        sinz = sin(angles[2])
        cosz = cos(angles[2])
        
        lines = [Vector.rotateVector(line, sinz, cosz) \
                 for line in [ [0, Display.ARM_LENGTH], \
                              [Display.ARM_LENGTH, 0], \
                              [0, -Display.ARM_LENGTH], \
                              [-Display.ARM_LENGTH, 0]] ] 
        
        for index in range(4):
            self._canvasXY.coords(self._linesXY[index], x, y, x+lines[index][0], y-lines[index][1])


    def _plotHeight(self, x, y, angle, canvas, lines):
    
        cosine = cos(angle)
        sine = sin(angle)
        
        vectors = [Vector.rotateVector(vector, sine, cosine) \
                 for vector in [[-Display.ARM_LENGTH, 0], \
                              [Display.ARM_LENGTH, 0]] ]
        
        for index in range(2):
            canvas.coords(lines[index], x, y, x+vectors[index][0], y+vectors[index][1])


    def _plotXZ(self, coord, angles):
        
        x = 100
        y = int(200.0 - (coord[2]*Display.PIXELS_METER%200.0))
        
        self._plotHeight(x, y, angles[1], self._canvasXZ, self._linesXZ)
        

    def _plotYZ(self, coord, angles):
        
        x = 100
        y = int(200.0 - (coord[2]*Display.PIXELS_METER%200.0))
        
        self._plotHeight(x, y, -angles[0], self._canvasYZ, self._linesYZ)


    def _refresh(self):
        
        if self._isRunning:
        
            state = self._stateProvider.getState()
            if not state._crashed:
                angles = [radians(angle) for angle in state._angles]
                self._plotXY(state._coords, angles)
                self._plotXZ(state._coords, angles)
                self._plotYZ(state._coords, angles)
                
            else:
                self._canvasXY.create_text((200,100), text="CRASHED!", fill="#ff0000")
                self._canvasXZ.create_text((100,100), text="CRASHED!", fill="#ff0000")
                self._canvasYZ.create_text((100,100), text="CRASHED!", fill="#ff0000")
            
            self.update_idletasks()
            
            self.after(int(self._refreshTime * 1000.0), self._refresh)
