# ChickenDoor
Fixing a broken automatic chicken door by replacing its electronics with an RPI Pico and some sensors.
<img src="IMG-20240610-WA0002.jpg" alt="state machine" width="900"/>

## Hardware
- Raspberry Pi Pico
- Light sensor
- Magnet Sensor
- Motor controller md08a
- Motor
- Button
- LEDs
<img src="IMG-20240610-WA0006.jpg" alt="electronics" width="300"/>

## Door Mechanism
The door itself is a metal sheet with a row of holes along its length. The teeth on the motor engage in these holes and move the plate up or down while the motor spins. The Door additionally includes a magnet on each side. Thanks to these magnets, a magnet sensor can be used to determine if the door has reached the open/close position and should be stopped.
Using a light sensor, the system is able to automatically open/close at the correct light level.
The LEDs indicate the current state, and the button can be used to manually change states.
<img src="IMG-20240514-WA0006.jpg" alt="state machine" width="900"/>
<img src="IMG-20240610-WA0003.jpg" alt="state machine" width="900"/>

## Settings & Wiring
In the first code block "Settings" in "main.py", you can specify settings like the light sample period or motor speed.
The second code block "IO pins" can be modified to select the correct Gpio pins for sensors etc. of your configuration.

<img src="IMG-20240514-WA0004.jpg" alt="state machine" width="500"/>
<img src="IMG-20240514-WA0005.jpg" alt="state machine" width="500"/>
<img src="IMG-20240610-WA0004.jpg" alt="state machine" width="500"/>
