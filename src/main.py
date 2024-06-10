from machine import Pin , PWM
from Motor_md08a import Motor_md08a as Motor
import utime
        
# Settings
LIGHT_SAMPLE_PERIOD = .5  # (sec)  delay between every light level check
LIGHT_CHANGE_DELAY = 600  # (sec)  how long should there be a consistent change in brightness before taking action
MIN_OPEN_TIME = 8         # (hour) only open the gate if it is later
OPEN = True               # (bool) initial state of the gate
MAGNET_COOLOFF = 2        # (sec)  min delay after magnet removal
BUTTON_COOLOFF = .1       # (sec)  min delay for next button press
MOTOR_SPEED = .75         # (0-1)  persentage of max possible speed
REDUCED_MOTOR_SPEED = .1  # (0-1)  persentage of max possible speed for closing the gate

# IO pins
motor = Motor(pin_PWM=22, pin_IN1=26, pin_IN2=27)
pin_light = Pin(21, mode=Pin.IN)
pin_button = Pin(17, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_magnet = Pin(19, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_led_green = Pin(18, mode=Pin.OUT)
pin_led_red = Pin(16, mode=Pin.OUT)
pin_led_green.value(OPEN)
pin_led_red.value(not OPEN)

# States
STATE_OPEN            = "STATE_OPEN"
STATE_CLOSING         = "STATE_CLOSING"
STATE_CLOSE           = "STATE_CLOSE"
STATE_OPENING         = "STATE_OPENING"
STATE_MANUAL_OPEN     = "STATE_MANUAL_OPEN"
STATE_MANUAL_CLOSING  = "STATE_MANUAL_CLOSING"
STATE_MANUAL_CLOSE    = "STATE_MANUAL_CLOSE"
STATE_MANUAL_OPENING  = "STATE_MANUAL_OPENING"

# State changes
CHANGE_BUTTON         = "CHANGE_BUTTON"
CHANGE_NO_LIGHT       = "CHANGE_NO_LIGHT"
CHANGE_LIGHT_AND_TIME = "CHANGE_LIGHT_AND_TIME"
CHANGE_MAGNET         = "CHANGE_MAGNET"

# Variables
state = STATE_OPEN if OPEN else STATE_CLOSED
time_since_light_off = None if not pin_light.value() else utime.time()
time_since_light_on  = None if     pin_light.value() else utime.time()
time_magnet_cooloff  = None if pin_magnet.value() else utime.time()
time_button_cooloff  = utime.time()
time_led_blink = utime.time()

# IO callbacks
def light_callback(pin):
    global time_since_light_on
    global time_since_light_off
    if pin.value():
        # light on -> off
        time_since_light_off = utime.time()
        time_since_light_on  = None
    else:
        # light off -> on
        time_since_light_off = None
        time_since_light_on  = utime.time()

def button_callback(pin):
    global time_button_cooloff
    if utime.time() - time_button_cooloff > BUTTON_COOLOFF:
        zustands_automat(CHANGE_BUTTON)
        time_button_cooloff = utime.time()

def magnet_callback(pin):
    global time_magnet_cooloff
    if pin.value():
        # magnet detected
        if time_magnet_cooloff != None and utime.time() - time_magnet_cooloff > MAGNET_COOLOFF:
            zustands_automat(CHANGE_MAGNET)
        time_magnet_cooloff = None
    else:
        # magnet lost
        
        time_magnet_cooloff = utime.time()

# Add callbacks as IO handlers
pin_light.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=light_callback)
pin_button.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)
pin_magnet.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=magnet_callback)

# state logic map; which CHANGE can change a STATE to which other STATE
state_logic = {
    STATE_OPEN            : {
        CHANGE_BUTTON:STATE_MANUAL_CLOSING,
        CHANGE_NO_LIGHT:STATE_CLOSING},
    STATE_CLOSING         : {
        CHANGE_BUTTON:STATE_MANUAL_OPENING,
        CHANGE_MAGNET:STATE_CLOSE},
    STATE_CLOSE           : {
        CHANGE_BUTTON:STATE_MANUAL_OPENING,
        CHANGE_LIGHT_AND_TIME:STATE_OPENING},
    STATE_OPENING         : {
        CHANGE_BUTTON:STATE_MANUAL_CLOSING,
        CHANGE_MAGNET:STATE_OPEN},
    STATE_MANUAL_OPEN     : {
        CHANGE_BUTTON:STATE_MANUAL_CLOSING,
        CHANGE_LIGHT_AND_TIME:STATE_OPEN},
    STATE_MANUAL_CLOSING  : {
        CHANGE_BUTTON:STATE_MANUAL_OPENING,
        CHANGE_MAGNET:STATE_MANUAL_CLOSE},
    STATE_MANUAL_CLOSE    : {
        CHANGE_BUTTON:STATE_MANUAL_OPENING,
        CHANGE_NO_LIGHT:STATE_CLOSE},
    STATE_MANUAL_OPENING  : {
        CHANGE_BUTTON:STATE_MANUAL_CLOSING,
        CHANGE_MAGNET:STATE_MANUAL_OPEN}
    }

# switching between states
def change_state(new_state):
    global state
    
    if state==STATE_CLOSING or state==STATE_MANUAL_CLOSING or state==STATE_OPENING or state==STATE_MANUAL_OPENING:
        motor.set_power(0)
        
    if   new_state==STATE_CLOSING:
        motor.set_power(REDUCED_MOTOR_SPEED)
        pin_led_green.on()
    elif new_state==STATE_MANUAL_CLOSING:
        motor.set_power(MOTOR_SPEED)
        pin_led_green.on()
    elif new_state==STATE_OPENING or new_state==STATE_MANUAL_OPENING:
        motor.set_power(MOTOR_SPEED * -1)
        pin_led_red.on()
    elif new_state==STATE_OPEN or new_state==STATE_CLOSE or new_state==STATE_MANUAL_OPEN or new_state==STATE_MANUAL_CLOSE:
        light_callback(pin_light)
        is_open = new_state==STATE_OPEN or new_state==STATE_MANUAL_OPEN 
        pin_led_green.value(is_open)
        pin_led_red.value(not is_open)
    if   new_state==STATE_OPENING or new_state==STATE_CLOSING or new_state==STATE_MANUAL_OPENING or new_state==STATE_MANUAL_CLOSING:
        magnet_callback(pin_magnet)
    
    state = new_state

# state logic function
def zustands_automat(state_change):
    print(state_change)
    if state_change in state_logic[state].keys():
        change_state(state_logic[state][state_change])
        print(state)
    print(" ")
    
# main loop
while True:
    # light timer
    t_on  = time_since_light_on
    t_off = time_since_light_off
    
    if t_on != None and utime.time() - t_on  > LIGHT_CHANGE_DELAY and utime.localtime()[3] >= MIN_OPEN_TIME:
        zustands_automat(CHANGE_LIGHT_AND_TIME)
        time_since_light_on  = None
    if t_off != None and utime.time() - t_off > LIGHT_CHANGE_DELAY:
        zustands_automat(CHANGE_NO_LIGHT)
        time_since_light_off = None
    
    # led blinking
    if utime.time() - time_led_blink >= 1:
        time_led_blink = utime.time()
        if state == STATE_OPENING or state == STATE_MANUAL_OPENING:
            pin_led_green.toggle()
        elif state == STATE_CLOSING or state == STATE_MANUAL_CLOSING:
            pin_led_red.toggle()
    
    utime.sleep(LIGHT_SAMPLE_PERIOD)

motor.deinit()