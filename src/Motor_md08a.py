from machine import Pin , PWM

class Motor_md08a():
    def __init__(self, pin_PWM, pin_IN1, pin_IN2):
        self.pin_PWM = PWM(Pin(pin_PWM, mode=Pin.OUT))
        self.pin_IN1 = Pin(pin_IN1, mode=Pin.OUT)
        self.pin_IN2 = Pin(pin_IN2, mode=Pin.OUT)
        
        self.pin_PWM.freq(100000) # 100kHz
        self.max_pwm = 65535
    
    def set_power(self,power):
        """ power from -1 to 1. Sign determents the direction """
        assert power >= -1 and power <= 1
        
        self.pin_IN1.value(power>0)
        self.pin_IN2.value(power<0)
        
        self.pin_PWM.duty_u16(int(self.max_pwm * abs(power)))
        
    def deinit(self):
        self.pin_IN1.off()
        self.pin_IN2.off()
        self.pin_PWM.duty_u16(0)
        self.pin_PWM.deinit()