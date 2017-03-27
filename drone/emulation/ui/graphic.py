# -*- coding: utf-8 -*-
'''
Created on 25 de feb. de 2016

@author: david
'''

import sys

if sys.version_info.major < 3:

    from Tkconstants import BOTH, DISABLED
    from Tkinter import Tk, Frame as tkFrame, Canvas, StringVar, Entry, Label
    from ttk import Frame as ttkFrame, Style
else:
    from tkinter.constants import BOTH, DISABLED
    from tkinter import Tk, Frame as tkFrame, Canvas, StringVar, Entry, Label
    from tkinter.ttk import Frame as ttkFrame, Style
    
from math import cos, sin, radians
from threading import Thread


from sensors.vector import Vector


class Display(ttkFrame):
    '''
    Displays the drone state on a graphical interface
    '''

    REFRESH_PERIOD = 0.2 #5Hz by default
    
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
        '''
        Set the flight state provider
        '''
        
        self._stateProvider = stateProvider
        
        return self
    
    
    def setLauncherMethod(self, launcherMethod):
        '''
        Set the method which controlls the process.
        
        It is required since the main thread (main loop) is used by the GUI. 
        Therefore, the process for the business logic must be executed within another thread. 
        '''
        
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
        
        #Draw frame

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

        
        #Info frame

        infoFrame = tkFrame(self)
        infoFrame.grid(column=1, row=0, sticky="NE", padx=4)

        #Angles
        Label(infoFrame, text="Coords").grid(column=0, row=0, sticky="WE")        
        self._coordTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._coordTexts[index], state=DISABLED, width=5).grid(column=index, row=1)

        #Angles
        Label(infoFrame, text="Angles").grid(column=0, row=2, sticky="WE")        
        self._angleTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._angleTexts[index], state=DISABLED, width=5).grid(column=index, row=3)
               
        #Accels
        Label(infoFrame, text="Accels").grid(column=0, row=4, sticky="WE")
        self._accelTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._accelTexts[index], state=DISABLED, width=5).grid(column=index, row=5)
        
        #Speeds
        Label(infoFrame, text="Speeds").grid(column=0, row=6, sticky="WE")
        self._speedTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._speedTexts[index], state=DISABLED, width=5).grid(column=index, row=7)
        
            
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

                for index in range(3):
                    self._coordTexts[index].set("{0:.3f}".format(state._coords[index]))
                    self._angleTexts[index].set("{0:.3f}".format(state._angles[index]))
                    self._accelTexts[index].set("{0:.3f}".format(state._accels[index]))
                    self._speedTexts[index].set("{0:.3f}".format(state._speeds[index]))
                
            else:
                self._canvasXY.create_text((200,100), text="CRASHED!", fill="#ff0000")
                self._canvasXZ.create_text((100,100), text="CRASHED!", fill="#ff0000")
                self._canvasYZ.create_text((100,100), text="CRASHED!", fill="#ff0000")
            
            self.update_idletasks()
            
            self.after(int(self._refreshTime * 1000.0), self._refresh)
