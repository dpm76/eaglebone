# -*- coding: utf-8 -*-

'''
Created on 10/05/2015

@author: david
'''
from Tkconstants import BOTH, VERTICAL, HORIZONTAL, LEFT, SUNKEN, DISABLED
from Tkinter import Frame as tkFrame, Canvas, Scale, DoubleVar, Checkbutton, \
    Label, Entry, Message, IntVar, OptionMenu, StringVar, Spinbox
from platform import system
from threading import Thread
import time
from ttk import Style, Frame as ttkFrame, Button

from communications.console import ConsoleLink
from communications.inet import INetLink
from config import Configuration


class Cockpit(ttkFrame):
    '''
    Remote controller GUI 
    '''
    
    #TODO: 20160415 DPM - Set these values from configuration file
    THROTTLE_BY_USER = False

    DEFAULT_DRONE_IP = "192.168.1.130"
    DEFAULT_DRONE_PORT = 2121
    #---
    

    KEY_ANG_SPEED = "ang-speed"
    KEY_ANGLES = "angles"
    KEY_ACCEL = "accel"
    
    PID_KEYS = ["P", "I", "D"]

    DIR_NONE = 0
    DIR_VERTICAL = 1
    DIR_HORIZONTAL = 2
    
    MAX_ACCEL = 10.0 #TODO currently angles. Replace by m/s² later
    MAX_ACCEL_Z = 1.0 #m/s² steps of 0.01 m/s²
    MAX_ANGLE_SPEED = 20.0 #º/s

    def __init__(self, parent, isDummy = False, droneIp = DEFAULT_DRONE_IP, dronePort = DEFAULT_DRONE_PORT):
        '''
        Constructor
        '''
        ttkFrame.__init__(self, parent)
        
        self._started = IntVar()
        self._integralsEnabled = IntVar()
        self._target = [0.0] * 4        
        
        self._selectedPidConstats = "--"
        self._pidConstants = {
                              Cockpit.KEY_ANG_SPEED:{
                                           "X":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                },
                                           "Y":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                },
                                           "Z":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                }
                                           },
                               Cockpit.KEY_ANGLES: {
                                          "X":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                },
                                           "Y":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                }
                                          },
                               Cockpit.KEY_ACCEL:{
                                           "X":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                },
                                           "Y":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                },
                                            "Z":{
                                                "P": 0.0,
                                                "I": 0.0,
                                                "D": 0.0
                                                 }
                                          }
                              }
        
        self.parent = parent

        self.initUI()

        self._controlKeysLocked = False

        if not isDummy:
            self._link = INetLink(droneIp, dronePort)
        else:
            self._link = ConsoleLink()
            
        self._link.open()

        self._updateInfoThread = Thread(target=self._updateInfo)
        self._updateInfoThreadRunning = False
        self._readingState = False

        self._start()
        
            
    def initUI(self):
        
        self.parent.title("Drone control")
        self.style = Style()
        self.style.theme_use("default")
        
        self.pack(fill=BOTH, expand=1)
        
        self.parent.bind_all("<Key>", self._keyDown)
        self.parent.bind_all("<KeyRelease>", self._keyUp)

        if system() == "Linux":
            self.parent.bind_all("<Button-4>", self._onMouseWheelUp)
            self.parent.bind_all("<Button-5>", self._onMouseWheelDown)

        else:
            #case of Windows
            self.parent.bind_all("<MouseWheel>", self._onMouseWheel)
        
        #Commands        
        commandsFrame = tkFrame(self)
        commandsFrame.grid(column=0, row=0, sticky="WE")
        
        self._startedCB = Checkbutton(commandsFrame, text="On", variable=self._started, command=self._startedCBChanged)
        self._startedCB.pack(side=LEFT, padx=4)
        
#         self._integralsCB = Checkbutton(commandsFrame, text="Int.", variable=self._integralsEnabled, \
#                                         command=self._integralsCBChanged, state=DISABLED)
#         self._integralsCB.pack(side=LEFT, padx=4)
        
        self._quitButton = Button(commandsFrame, text="Quit", command=self.exit)
        self._quitButton.pack(side=LEFT, padx=2, pady=2)
        
#         self._angleLbl = Label(commandsFrame, text="Angle")
#         self._angleLbl.pack(side=LEFT, padx=4)
#         
#         self._angleEntry = Entry(commandsFrame, state=DISABLED)
#         self._angleEntry.pack(side=LEFT)
        
        #Info
        infoFrame = tkFrame(self)
        infoFrame.grid(column=1, row=1, sticky="NE", padx=4)
        
        #Throttle
        Label(infoFrame, text="Throttle").grid(column=0, row=0, sticky="WE")        
        self._throttleTexts = [StringVar(),StringVar(),StringVar(),StringVar()]
        Entry(infoFrame, textvariable=self._throttleTexts[3], state=DISABLED, width=5).grid(column=0, row=1)                
        Entry(infoFrame, textvariable=self._throttleTexts[0], state=DISABLED, width=5).grid(column=1, row=1)
        Entry(infoFrame, textvariable=self._throttleTexts[2], state=DISABLED, width=5).grid(column=0, row=2)
        Entry(infoFrame, textvariable=self._throttleTexts[1], state=DISABLED, width=5).grid(column=1, row=2)
        
        #Angles
        Label(infoFrame, text="Angles").grid(column=0, row=3, sticky="WE")        
        self._angleTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._angleTexts[index], state=DISABLED, width=5).grid(column=index, row=4)
               
        #Accels
        Label(infoFrame, text="Accels").grid(column=0, row=5, sticky="WE")
        self._accelTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._accelTexts[index], state=DISABLED, width=5).grid(column=index, row=6)
        
        #Speeds
        Label(infoFrame, text="Speeds").grid(column=0, row=7, sticky="WE")
        self._speedTexts = [StringVar(),StringVar(),StringVar()]
        for index in range(3):
            Entry(infoFrame, textvariable=self._speedTexts[index], state=DISABLED, width=5).grid(column=index, row=8)
        
        #Height
        Label(infoFrame, text="Height").grid(column=0, row=9, sticky="W")
        self._heightText = StringVar()
        Entry(infoFrame, state=DISABLED, width=5).grid(column=1, row=9)
        
        #control
        
        controlFrame = tkFrame(self)
        controlFrame.grid(column=0, row=1, sticky="W")
        
        self._throttle = DoubleVar()
        
        if Cockpit.THROTTLE_BY_USER:

            self._thrustScale = Scale(controlFrame, orient=VERTICAL, from_=100.0, to=0.0, \
                                tickinterval=0, variable=self._throttle, resolution=0.1, \
                                length=200, showvalue=1, \
                                state=DISABLED,
                                command=self._onThrustScaleChanged)

        else:
        
            self._thrustScale = Scale(controlFrame, orient=VERTICAL, from_=100.0, to=-100.0, \
                                tickinterval=0, variable=self._throttle, \
                                length=200, showvalue=1, \
                                state=DISABLED,
                                command=self._onThrustScaleChanged)

        self._thrustScale.bind("<Double-Button-1>", self._onThrustScaleDoubleButton1, "+")
        self._thrustScale.grid(column=0)
        
        self._shiftCanvas = Canvas(controlFrame, bg="white", height=400, width=400, \
                             relief=SUNKEN)
        self._shiftCanvas.bind("<Button-1>", self._onMouseButton1)
        #self._shiftCanvas.bind("<ButtonRelease-1>", self._onMouseButtonRelease1)
        self._shiftCanvas.bind("<B1-Motion>", self._onMouseButton1Motion)
        self._shiftCanvas.bind("<Double-Button-1>", self._onMouseDoubleButton1)

        self._shiftCanvas.bind("<Button-3>", self._onMouseButton3)
        #self._shiftCanvas.bind("<ButtonRelease-3>", self._onMouseButtonRelease3)
        self._shiftCanvas.bind("<B3-Motion>", self._onMouseButton3Motion)

        self._shiftCanvas.grid(row=0,column=1, padx=2, pady=2)
        self._shiftCanvas.create_oval(2, 2, 400, 400, outline="#ff0000")
        self._shiftCanvas.create_line(201, 2, 201, 400, fill="#ff0000")
        self._shiftCanvas.create_line(2, 201, 400, 201, fill="#ff0000")
        self._shiftMarker = self._shiftCanvas.create_oval(197, 197, 205, 205, outline="#0000ff", fill="#0000ff")
        
        self._yaw = DoubleVar()
        self._yawScale = Scale(controlFrame, orient=HORIZONTAL, from_=-100.0, to=100.0, \
                            tickinterval=0, variable=self._yaw, \
                            length=200, showvalue=1, \
                            command=self._onYawScaleChanged)
        self._yawScale.bind("<Double-Button-1>", self._onYawScaleDoubleButton1, "+")
        self._yawScale.grid(row=1, column=1)
        
        self._controlKeyActive = False
        

        #PID calibration

        pidCalibrationFrame = tkFrame(self)
        pidCalibrationFrame.grid(column=0, row=2, sticky="WE");

        self._pidSelected = StringVar()
        self._pidSelected.set("--")
        self._pidListBox = OptionMenu(pidCalibrationFrame, self._pidSelected, "--", \
                                      Cockpit.KEY_ANG_SPEED, Cockpit.KEY_ANGLES, Cockpit.KEY_ACCEL, \
                                       command=self._onPidListBoxChanged)
        self._pidListBox.pack(side=LEFT, padx=2)
        self._pidListBox.config(width=10)
        
        self._axisSelected = StringVar()
        self._axisSelected.set("--")
        self._axisListBox = OptionMenu(pidCalibrationFrame, self._axisSelected, "--", "X", "Y", "Z", \
                                       command=self._onAxisListBoxChanged)
        self._axisListBox.pack(side=LEFT, padx=2)
        self._axisListBox.config(state=DISABLED)

        Label(pidCalibrationFrame, text="P").pack(side=LEFT, padx=(14, 2))

        self._pidPString = StringVar()
        self._pidPString.set("0.00")
        self._pidPSpinbox = Spinbox(pidCalibrationFrame, width=5, from_=0.0, to=100.0, increment=0.01, state=DISABLED, \
                                         textvariable=self._pidPString, command=self._onPidSpinboxChanged)
        self._pidPSpinbox.pack(side=LEFT, padx=2)

        Label(pidCalibrationFrame, text="I").pack(side=LEFT, padx=(14, 2))

        self._pidIString = StringVar()
        self._pidIString.set("0.00")
        self._pidISpinbox = Spinbox(pidCalibrationFrame, width=5, from_=0.0, to=100.0, increment=0.01, state=DISABLED, \
                                         textvariable=self._pidIString, command=self._onPidSpinboxChanged)
        self._pidISpinbox.pack(side=LEFT, padx=2)
        
        Label(pidCalibrationFrame, text="D").pack(side=LEFT, padx=(14, 2))
        
        self._pidDString = StringVar()
        self._pidDString.set("0.00")
        self._pidDSpinbox = Spinbox(pidCalibrationFrame, width=5, from_=0.0, to=100.0, increment=0.01, state=DISABLED, \
                                         textvariable=self._pidDString, command=self._onPidSpinboxChanged)
        self._pidDSpinbox.pack(side=LEFT, padx=2)
        
        #debug
        debugFrame = tkFrame(self)
        debugFrame.grid(column=0, row=3, sticky="WE")
        
        self._debugMsg = Message(debugFrame, anchor="nw", justify=LEFT, relief=SUNKEN, width=300)
        self._debugMsg.pack(fill=BOTH, expand=1)



    def _start(self):

        self._readDroneConfig()
        
    
    def exit(self):
        
        self._link.send({"key": "close", "data": None})
        
        self._stopUpdateInfoThread()
        
        self._link.close()

        self.quit()


    def _updateTarget(self):
        
        markerCoords = self._shiftCanvas.coords(self._shiftMarker)
        coords = ((markerCoords[0] + markerCoords[2]) / 2, (markerCoords[1] + markerCoords[3]) / 2)
        
        self._target[1] = float(coords[0] - 201) * Cockpit.MAX_ACCEL / 200.0
        self._target[0] = float(coords[1] - 201) * Cockpit.MAX_ACCEL / 200.0      
        #Remote control uses clockwise angle, but the drone's referece system uses counter-clockwise angle
        self._target[2] = -self._yaw.get() * Cockpit.MAX_ANGLE_SPEED / 100.0
        
        if Cockpit.THROTTLE_BY_USER:
            self._target[3] = 0.0
        else:        
            self._target[3] = self._throttle.get() * Cockpit.MAX_ACCEL_Z / 100.0
        
        self._sendTarget() 
    
        
    def _keyDown(self, event):

        if event.keysym == "Escape":            
            self._throttle.set(0)
            self._started.set(0)
            self._thrustScale.config(state=DISABLED)
            self._stopUpdateInfoThread()
            self._sendIsStarted()
            
        elif event.keysym.startswith("Control"):            
            self._controlKeyActive = True
            
        elif not self._controlKeysLocked and self._controlKeyActive:
            
            if event.keysym == "Up":
                self._thrustScaleUp()
                
            elif event.keysym == "Down":
                self._thrustScaleDown()
                
            elif event.keysym == "Left":
                self._yawLeft()
                
            elif event.keysym == "Right":
                self._yawRight()
                
            elif event.keysym == "space":
                self._yawReset()
                if not Cockpit.THROTTLE_BY_USER:
                    self._thrustReset()
                
        elif not self._controlKeysLocked and not self._controlKeyActive:
            
            if event.keysym == "Up":
                self._moveShiftCanvasMarker((0,-5))
                
            elif event.keysym == "Down":
                self._moveShiftCanvasMarker((0,5))
                
            elif event.keysym == "Left":
                self._moveShiftCanvasMarker((-5,0))
                
            elif event.keysym == "Right":
                self._moveShiftCanvasMarker((5,0))
                
            elif event.keysym == "space":
                self._resetShiftCanvasMarker()                
    
    
    def _keyUp(self, eventArgs):
        
        if eventArgs.keysym.startswith("Control"):
            self._controlKeyActive = False
            
    
    def _onMouseButton1(self, eventArgs):

        self._lastMouseCoords = (eventArgs.x, eventArgs.y)

        
    def _onMouseButtonRelease1(self, eventArgs):

        self._shiftCanvas.coords(self._shiftMarker, 197, 197, 205, 205)

    
    def _limitCoordsToSize(self, coords, size):
        
        if coords[0] > size:
            x = size
        
        elif coords[0] < 0:
            x = 0
            
        else:
            x = coords[0]
            
            
        if coords[1] > size:
            y = size
            
        elif coords[1] < 0:
            y = 0
            
        else:
            y = coords[1]
            
        
        return (x,y)
    
    
    def _moveShiftCanvasMarker(self, shift):

        lastCoords = self._shiftCanvas.coords(self._shiftMarker)
        newCoords = (lastCoords[0] + shift[0], lastCoords[1] + shift[1])        
        newCoords = self._limitCoordsToSize(newCoords, 400)
    
        self._shiftCanvas.coords(self._shiftMarker, newCoords[0], newCoords[1], newCoords[0] + 8, newCoords[1] + 8)
        self._updateTarget()
    
    
    def _resetShiftCanvasMarker(self):
    
        self._shiftCanvas.coords(self._shiftMarker, 197, 197, 205, 205)
        self._updateTarget()
        
    
    def _onMouseButton1Motion(self, eventArgs):

        deltaCoords = (eventArgs.x - self._lastMouseCoords[0], eventArgs.y - self._lastMouseCoords[1])
        self._moveShiftCanvasMarker(deltaCoords)
        self._lastMouseCoords = (eventArgs.x, eventArgs.y)
  
      
    def _onMouseDoubleButton1(self, eventArgs):
        
        self._resetShiftCanvasMarker()        
            

    def _onMouseButton3(self, eventArgs):

        self._lastMouseCoords = (eventArgs.x, eventArgs.y)
        self._mouseDirection = Cockpit.DIR_NONE

        
    def _onMouseButtonRelease3(self, eventArgs):

        self._shiftCanvas.coords(self._shiftMarker, 197, 197, 205, 205)

        
    def _onMouseButton3Motion(self, eventArgs):

        deltaCoords = (eventArgs.x - self._lastMouseCoords[0], eventArgs.y - self._lastMouseCoords[1])

        if self._mouseDirection == Cockpit.DIR_NONE:
            if abs(deltaCoords[0]) > abs(deltaCoords[1]):
                self._mouseDirection = Cockpit.DIR_HORIZONTAL
            else:
                self._mouseDirection = Cockpit.DIR_VERTICAL

        if self._mouseDirection == Cockpit.DIR_HORIZONTAL:
            deltaCoords = (deltaCoords[0], 0)
        else:
            deltaCoords = (0, deltaCoords[1])

        self._moveShiftCanvasMarker(deltaCoords)
        self._lastMouseCoords = (eventArgs.x, eventArgs.y)
        
    
    def _thrustScaleUp(self):

        if self._started.get(): 
            newValue = self._thrustScale.get() \
                + (0.1 if Cockpit.THROTTLE_BY_USER else 1.0)
            self._thrustScale.set(newValue)
            
            self._updateTarget()
    
    
    def _thrustScaleDown(self):
        
        if self._started.get():
            newValue = self._thrustScale.get() \
                - (0.1 if Cockpit.THROTTLE_BY_USER else 1.0)
            self._thrustScale.set(newValue)
            
            self._updateTarget()
            
    
    def _thrustReset(self):
        
        if self._started.get():
            self._thrustScale.set(0.0)
            
            self._updateTarget()
            
            
    def _onThrustScaleDoubleButton1(self, eventArgs):
        
        self._thrustReset()
        
        return "break"
        
    
    def _yawRight(self):
        
        newValue = self._yaw.get() + 1
        self._yaw.set(newValue)
        self._updateTarget()
            

    def _yawLeft(self):
        
        newValue = self._yaw.get() - 1
        self._yaw.set(newValue)
        self._updateTarget()
        
        
    def _yawReset(self):
        
        self._yaw.set(0)
        self._updateTarget()
        
        
    def _onMouseWheelUp(self, eventArgs):
        
        if not self._controlKeyActive:
            self._thrustScaleUp()
            
        else:
            self._yawRight()
            

    def _onMouseWheelDown(self, eventArgs):

        if not self._controlKeyActive:
            self._thrustScaleDown()
            
        else:
            self._yawLeft()
    

    def _onMouseWheel(self, eventArgs):

        factor = eventArgs.delta/(1200.0 if Cockpit.THROTTLE_BY_USER and not self._controlKeyActive else 120.0)

        if not self._controlKeyActive:
        
            if self._started.get():
                newValue = self._thrustScale.get() + factor 
                self._thrustScale.set(newValue)
                
                self._updateTarget()
        else:
            newValue = self._yaw.get() + factor
            self._yaw.set(newValue)
            self._updateTarget()

    
    def _onYawScaleChanged(self, eventArgs):
        
        self._updateTarget()
    
    
    def _onYawScaleDoubleButton1(self, eventArgs):
        
        self._yawReset()
        
        return "break"
        
    
    def _startedCBChanged(self):
        
        if not self._started.get():
            self._throttle.set(0)
            self._thrustScale.config(state=DISABLED)            
            #self._integralsCB.config(state=DISABLED)
            self._stopUpdateInfoThread()
        else:
            self._thrustScale.config(state="normal")            
            #self._integralsCB.config(state="normal")
            self._startUpdateInfoThread()
            
        self._sendIsStarted()
     
    
#     def _integralsCBChanged(self):
#     
#         self._link.send({"key": "integrals", "data":self._integralsEnabled.get() != 0})
#             
    
     
    def _onThrustScaleChanged(self, eventArgs):
        
        if Cockpit.THROTTLE_BY_USER:
            
            self._sendThrottle()
        
        else:
        
            self._updateTarget()


    def _sendThrottle(self):
        
        self._link.send({"key": "throttle", "data": self._throttle.get()})
    

    def _sendTarget(self):
        
        self._link.send({"key": "target", "data": self._target})
        
        
    def _sendIsStarted(self):
        
        isStarted = self._started.get() != 0        
        self._link.send({"key": "is-started", "data": isStarted})
        

    def _sendPidCalibrationData(self):

        if self._pidSelected.get() != "--" and self._axisSelected.get() != "--":

            pidData = {
                "pid": self._pidSelected.get(),
                "axis": self._axisSelected.get(), 
                "p": float(self._pidPSpinbox.get()),
                "i": float(self._pidISpinbox.get()),
                "d": float(self._pidDSpinbox.get())}
        
            self._link.send({"key": "pid-calibration", "data": pidData})


    def _updatePidCalibrationData(self):

        pid = self._pidSelected.get()
        axis = self._axisSelected.get()

        if pid != "--" and axis != "--":
             
            self._pidConstants[pid][axis]["P"] = float(self._pidPSpinbox.get())
            self._pidConstants[pid][axis]["I"] = float(self._pidISpinbox.get())
            self._pidConstants[pid][axis]["D"] = float(self._pidDSpinbox.get())
            

    def _readDroneConfig(self):

        self._link.send({"key": "read-drone-config", "data": None}, self._onDroneConfigRead)


    def _readDroneState(self):
        
        if not self._readingState:
            self._readingState = True
            self._link.send({"key": "read-drone-state", "data": None}, self._onDroneStateRead)


    def _readPidConfigItem(self, message, cockpitKey, axises, configKeys):
        
        for i in range(len(axises)):
            for j in range(len(Cockpit.PID_KEYS)):
                self._pidConstants[cockpitKey][axises[i]][Cockpit.PID_KEYS[j]] = message[configKeys[j]][i]
                

    def _onDroneConfigRead(self, message):

        #TODO Show current configuration within the GUI (at least relevant settings)
        if message:
            
            #Angle-speeds
            self._readPidConfigItem(message, Cockpit.KEY_ANG_SPEED, ["X", "Y", "Z"], \
                                    [Configuration.PID_ANGLES_SPEED_KP, \
                                     Configuration.PID_ANGLES_SPEED_KI, \
                                     Configuration.PID_ANGLES_SPEED_KD])
            
            #Angles
            self._readPidConfigItem(message, Cockpit.KEY_ANGLES, ["X", "Y"], \
                                    [Configuration.PID_ANGLES_KP, \
                                     Configuration.PID_ANGLES_KI, \
                                     Configuration.PID_ANGLES_KD])
                        
            #Accels
            self._readPidConfigItem(message, Cockpit.KEY_ACCEL, ["X", "Y", "Z"], \
                                    [Configuration.PID_ACCEL_KP, \
                                     Configuration.PID_ACCEL_KI, \
                                     Configuration.PID_ACCEL_KD])
        

    def _onDroneStateRead(self, state):
        
        if state:
            for index in range(4):
                self._throttleTexts[index].set("{0:.3f}".format(state["_throttles"][index]))
                
            for index in range(3):
                self._accelTexts[index].set("{0:.3f}".format(state["_accels"][index]))
                self._angleTexts[index].set("{0:.3f}".format(state["_angles"][index]))
                
        else:
            self._stopUpdateInfoThread()
            
        self._readingState = False
   

    def _onPidSpinboxChanged(self):

        self._updatePidCalibrationData()
        self._sendPidCalibrationData()

    
    def _onPidListBoxChanged(self, pid):
        
        self._axisSelected.set("--")
        
        self._pidPString.set("--")
        self._pidIString.set("--")
        self._pidDString.set("--")

        self._pidPSpinbox.config(state=DISABLED)
        self._pidISpinbox.config(state=DISABLED)
        self._pidDSpinbox.config(state=DISABLED)

        self._selectedPidConstats = pid

        if pid == "--":
            self._axisListBox.config(state=DISABLED)
            self._controlKeysLocked = False
                       
        else:
            self._axisListBox.config(state="normal")
            self._controlKeysLocked = True


    def _onAxisListBoxChanged(self, axis):
        
        if axis == "--" or (self._selectedPidConstats == Cockpit.KEY_ANGLES and axis == "Z"):
            
            self._pidPString.set("--")
            self._pidIString.set("--")
            self._pidDString.set("--")
            
            self._pidPSpinbox.config(state=DISABLED)
            self._pidISpinbox.config(state=DISABLED)
            self._pidDSpinbox.config(state=DISABLED)
            
            self._controlKeysLocked = axis != "--"
            
        else:
            
            self._pidPString.set("{:.2f}".format(self._pidConstants[self._selectedPidConstats][axis]["P"]))
            self._pidIString.set("{:.2f}".format(self._pidConstants[self._selectedPidConstats][axis]["I"]))
            self._pidDString.set("{:.2f}".format(self._pidConstants[self._selectedPidConstats][axis]["D"]))
            
            self._pidPSpinbox.config(state="normal")
            self._pidISpinbox.config(state="normal")
            self._pidDSpinbox.config(state="normal")
            
            self._controlKeysLocked = True

            
    def _updateInfo(self):
        
        while self._updateInfoThreadRunning:
            
            self._readDroneState()
            
            time.sleep(1.0)
            

    def _startUpdateInfoThread(self):
        
        self._updateInfoThreadRunning = True
        if not self._updateInfoThread.isAlive():                
            self._updateInfoThread.start()
        
            
    def _stopUpdateInfoThread(self):
        
        self._updateInfoThreadRunning = False
        if self._updateInfoThread.isAlive():
            self._updateInfoThread.join()
    