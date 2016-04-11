# EagleBone

Open-source modular flight controller for quadcopters based on Beagle-Bone.


##Goals

This project develops a framework to provide flight stabilization and controlling for drones configured as quadcopter, using so less additional hardware as possible. Because this reason, it is focused on BeagleBone platform, since it is based on the ARM7 Cortex A8 architecture, providing the required calculation performance to reach a right flight stabilization. At the same time the BeagleBone provides the required hardware interfaces to assembly the drone's components almost directly to the device. This is I2C for sensors, PWM output to control motors, GPIO for digital controlling, and more.

"Modular" means that any software component, such sensors, motor driver or flight controller, can be replaced in order to be customized in order to be adapted to the actual user requirements.

The choosed programming language for this project is Python, since it let a quick prototyping development with a low learning curve, meanwhile it can be easly integrated with C/C++ libraries for high-end performance features.


##Description

###Drone

This is the main application. It contains the core of the system, which can be extended with custom components. It perfoms flight stabilization and feed-back with the user through its API.


###Desktop Remote Control

This reposiry includes a simple remote controller application. It covers the basic functionality in order to flight the drone. The purpouse of this remote controller is to get a first approach to the EagleBone's drone controller system and test it. For a further use of the system, please, use a more advanced remote control application.


###Emulator

For those who want to understand the behavior of drones using different PID constants, but real drone crashing is not desired, the emulation application can be used. Additionaly, it can be used in order to accurate the real drone's PID constants before flighting it. It provides a basic interface, but enough to emulate drone flight.

Since the drone emulator can be executed on whatever computer running Python platform, it can be also used in order to evaluate the EagleBone drone flight system, on any personal computer.


###Running the components

####Running the emulator

Probably the reader's intention is running the Emulator application in order to test the EagleBone drone flight sytem, since it can be executed on any personal computer instead of a BeagleBone device.


#####Prerequisites

<ul>
<li><a href="https://www.python.org/">Python 2.7</a></li>
</ul>


#####Intructions

Include the EagleBone's installation path into the PYTHONPATH environment variable:

<code>$ export PYTHONPATH=$PYTHONPATH:./drone</code>

This makes to be searching within the current working path, inside the directory "drone". Therefore change the current directory path, as instance:

<code>$ cd ~/EagleBone</code>

The first time you run it, create a new configuration file first. The configuration file is a regular JSON file containing some parameters such PID constants or the sensor or motor driver to use. 

In order to create a new configuration file, you can copy and then modify the example file:

<code>$ cp example-drone.config.json drone.config.json</code>

The contents of this file should look like:

<code>
{"PID_ACCEL_KP": [0.0, 0.0, 4.0], "PID_ANGLES_KP": [2.0, 2.0], "PID_ANGLES_SPEED_KI": [1.7, 1.7, 0.1], "imu-class": "emulation", "PID_ANGLES_SPEED_KD": [0.0, 0.0, 0.0], "PID_ACCEL_KD": [0.0, 0.0, 0.0], "PID_ANGLES_KD": [0.0, 0.0], "motor-class": "emulation", "PID_ANGLES_KI": [1.7, 1.7], "PID_ACCEL_KI": [0.0, 0.0, 3.5], "remote-address": "localhost", "PID_ANGLES_SPEED_KP": [2.0, 2.0, 0.15]}
</code>

Notice that the parameters "imu-class" and "motor-class" are set as "emulation". This is required in order to run in an emulated environment.

Finally, launch the application:

<code>$ python drone/emulation/start.py</code>

The console will display the message "Waiting for remote control..." and a new window with two squares on top and one rectangle at the bottom is shown. Otherwise, please check the previous steps.

The top-left square shows the heigh and pitch angle. The top-right square shows the heigh and roll angle. And the bottom rectangle shows the XY-coordinates of the emulated drone and its yaw angle.

This emulated drone can be controlled by the Desktop Remote Controller also included in this repository. Please read its section within this document in order to know more details.


####Running the core system

This quick instructions tells how to run on the BeagleBone. If your intention is run the emulator on whatever computer platform supporting python, please, see the previous section. We assume that all hardware is well connected and configured. Please, connect all hardware components meanwhile the device is off. Otherwise it could be damaged.

#####Prerequisites

<ul>
<li>Standard drone components: ESC brushless motor controller, brushless motor, propellers, etc.</li>
<li>BeagleBone device</li>
<li>OS (official BeagleBone's Ubuntu console-only distribution is recommended)</li>
<li>Inertial Measurement Unit/Motion Processor Unit (currently implemented the IMU/MPU-6050)</li>
<li>Wireless network infrastructure (such WiFi or Bluetooth) [see note 1]</li>
<li><a href="https://www.python.org/">Python 2.7</a></li>
<li><a href="https://pypi.python.org/pypi/smbus-cffi">SMBus</a></li>
</ul>

Note 1: <i>The configuration of the communication system between the drone device and the remote controller device is out of the scope of this project.</i>


#####Instructions

Turn on the BeagleBone and access through a terminal session.

The first step is to install the contents of this repository into a directory. Clone or unzip the last version from this repository.

Since the access to the BeagleBone's I2C and PWM interfaces requires root privileges, run all steps as root or use the "sudo" command. Also, we'll use the "~/drone" directory as the EagleBone path. Anyway, the user can choose a different one.

Change the working path to the EagleBone installation directory. For example:

<code># cd ~/drone</code>

For the first time, configure the drone application creating a file "drone.config.json" in the installation directory. The easy way is copy the example configuration file as follows:

<code># cp example-drone.config.json drone.config.json</code>

The configuration is a regular JSON file. The points to configure are:

<ul>
<li>PID constants</li>
<li>Sensors</li>
<li>Motor driver</li>
</ul>

As a file example could be:

<code>
{"PID_ACCEL_KP": [0.0, 0.0, 4.0], "PID_ANGLES_KP": [2.0, 2.0], "PID_ANGLES_SPEED_KI": [1.75, 1.75, 0.1], "imu-class": "imu6050", "PID_ANGLES_SPEED_KD": [0.0, 0.0, 0.0], "PID_ACCEL_KD": [0.0, 0.0, 0.0], "PID_ANGLES_KD": [0.0, 0.0], "motor-class": "local", "PID_ANGLES_KI": [1.75, 1.75], "PID_ACCEL_KI": [0.0, 0.0, 3.0], "remote-address": "localhost", "PID_ANGLES_SPEED_KP": [2.0, 2.0, 0.15]}
</code>

Please, take into account that the former PID constants configuration may NOT work in your actual drone configuration properly. It is highly recommended to callibrate the PID constans in a safe environment before an outdoor flight, because a bad PID constants callibration could make the flight unstable and hence causing damages. Another possibility is simulating the real drone and trying with different constants values until the flight becomes stable and safe enough.

Once the configuration is done, the next step is initialize the PWM interface and export the python-path. It can be easily done typing:

<code># ./init-motor.sh</code>

Finally, the flight system and the remote controller server can be started up by:

<code># python drone/remote_control/start.py</code>

If you see the message "Waiting for remote control...", it means that the EagleBone system is running. Otherwise, check the previous steps.

In order to give commands to your drone, use a remote controller such the Desktop Remote Controller from a regular computer, which is also included in this repository. Please, read the next section for quick instructions about the Desktop Remote Controller application.

To finish the EagleBone system, just press CTRL+C.


####Desktop Remote Controller

Set the python path:

<code>$ export PYTHONPATH=$PYTHONPATH:./drone:./desktopRemoteControl</code>

This makes looking for the code with in the both directories from the current working directory. Hence, change the directory to the EagleBone's installation directory, for example:

<code>$ cd ~/EagleBone</code>

The remote control application needs the address of the drone's server. Please, check the BeagleBone device address before continue. In case of you are running the emulator on the same computer you can provide the "127.0.0.1" IP-address:

<code>$ python remoteDesktopControl/control.py --ip 127.0.0.1</code>

Or in case of real drone, assuming the IP is 192.168.1.130, for example:

<code>$ python remoteDesktopControl/control.py --ip 192.168.1.130</code>

The checkbox at the top-left is used to start the drone or finish it. Set it checked in order start your drone. Additionally the escape-key makes this checkbox to be unchecked, hence the drone will finish immediately.

The scrollbars, one horizontal at the left and the other vertical almost at the bottom, controls: the vertical one, set the desired vertical acceleration of the drone; and the horizontal one, controls the yaw speed. Those can be controled pressing the "control"-key and arrow-keys, once the drone is started.

The big circle with a cross is the drone's directional control. It can be controlled with the mouse, but also with the arrow-keys.

Finally, the controls at the window's bottom, are intended to change the PID constants during the flight. Since change them can make the flight unstable, don't use them with any real drone. Actually the purpouse is to experiment with an emulated drone.

Once the drone is finished (the top-left checkbox is unchecked), can close the remote control with the "Quit" button.
