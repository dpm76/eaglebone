'''
Created on 20 de ene. de 2016

@author: david
'''
import json
from os import path


class Configuration(object):
    
    FILE_PATH = "./drone.config.json"
    
    KEY_MOTOR_CLASS = "motor-class"
    VALUE_MOTOR_CLASS_LOCAL = "local"
    VALUE_MOTOR_CLASS_REMOTE = "remote"
    VALUE_MOTOR_CLASS_DUMMY = "dummy"
    VALUE_MOTOR_CLASS_EMULATION = "emulation"
    
    KEY_IMU_CLASS = "imu-class"
    VALUE_IMU_CLASS_3000 = "imu3000"
    VALUE_IMU_CLASS_6050 = "imu6050"
    VALUE_IMU_CLASS_REMOTE = "remote"
    VALUE_IMU_CLASS_3000EMU = "imu3000emu"
    VALUE_IMU_CLASS_DUMMY = "dummy"
    VALUE_IMU_CLASS_EMULATION = "emulation"
    
    KEY_REMOTE_ADDRESS = "remote-address"
    
    PID_ANGLES_SPEED_KP = "PID_ANGLES_SPEED_KP"
    PID_ANGLES_SPEED_KI = "PID_ANGLES_SPEED_KI"
    PID_ANGLES_SPEED_KD = "PID_ANGLES_SPEED_KD"
    
    PID_ANGLES_KP = "PID_ANGLES_KP"
    PID_ANGLES_KI = "PID_ANGLES_KI"
    PID_ANGLES_KD = "PID_ANGLES_KD"
    
    PID_ACCEL_KP = "PID_ACCEL_KP"
    PID_ACCEL_KI = "PID_ACCEL_KI"
    PID_ACCEL_KD = "PID_ACCEL_KD"
    
    KEY_MAX_ANGLE_X = "MAX_ANGLE_X"
    KEY_MAX_ANGLE_Y = "MAX_ANGLE_Y"
    KEY_MAX_ANGLE_SPEED_X = "MAX_ANGLE_SPEED_X"
    KEY_MAX_ANGLE_SPEED_Y = "MAX_ANGLE_SPEED_Y"
    KEY_MAX_ANGLE_SPEED_Z = "MAX_ANGLE_SPEED_Z"

    
    DEFAULT_CONFIG = {
                      KEY_MOTOR_CLASS: VALUE_MOTOR_CLASS_DUMMY,
                      KEY_IMU_CLASS: VALUE_IMU_CLASS_DUMMY,
                      
                      KEY_REMOTE_ADDRESS: "localhost",
                      
                      PID_ANGLES_SPEED_KP: [0.0, 0.0, 0.0], 
                      PID_ANGLES_SPEED_KI: [0.0, 0.0, 0.0],  
                      PID_ANGLES_SPEED_KD: [0.0, 0.0, 0.0],
                      
                      PID_ANGLES_KP: [0.0, 0.0],  
                      PID_ANGLES_KI: [0.0, 0.0],  
                      PID_ANGLES_KD: [0.0, 0.0],
                      
                      PID_ACCEL_KP: [0.0, 0.0, 0.0],  
                      PID_ACCEL_KI: [0.0, 0.0, 0.0],  
                      PID_ACCEL_KD: [0.0, 0.0, 0.0],
                      
                      KEY_MAX_ANGLE_X: 0.0,
                      KEY_MAX_ANGLE_Y: 0.0,
                      KEY_MAX_ANGLE_SPEED_X: 0.0,
                      KEY_MAX_ANGLE_SPEED_Y: 0.0,
                      KEY_MAX_ANGLE_SPEED_Z: 0.0
                      }
    
    _instance = None
    
    @staticmethod
    def getInstance():
        
        if Configuration._instance == None:
            Configuration._instance = Configuration()
            
        return Configuration._instance
    

    def __init__(self):
        
        #Read stored config from file
        self._config = Configuration.DEFAULT_CONFIG.copy()
        
        if path.exists(Configuration.FILE_PATH):
    
            with open(Configuration.FILE_PATH, "r") as configFile:
                serializedConfig = " ".join(configFile.readlines())
                configFile.close()
                
            storedConfig = json.loads(serializedConfig)
            
            #Replace default config by stored config
            for key in self._config.keys():
                
                if key in storedConfig:
                    
                    self._config[key] = storedConfig[key]
                    
        #Write current config into file
        self.writeFile(Configuration.FILE_PATH)
            

    def writeFile(self, filePath):
        '''
        Writes current config into file.
        @param filePath: Filepath where to store the current configuration.  
        '''
        
        serializedConfig = json.dumps(self._config)        
        with open(filePath, "w+") as configFile:
            configFile.write(serializedConfig + "\n")
            configFile.close()
            
            
    def getConfig(self):
        
        return self._config
