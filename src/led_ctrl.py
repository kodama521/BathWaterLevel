import RPi.GPIO as gpio
import threading

class LedControler(object):
    __DEFAULT_BLINK_INTERVAL = 1 #sec
    __DEFAULT_PWM_DUTY = 50
    def __init__(self, pin, on_state):
        self.__pin = pin
        self.__blink_interval = LedControler.__DEFAULT_BLINK_INTERVAL
        self.__on_state = on_state
        self.__off_state = ~on_state & 0x01
        self.__pin_state = self.__off_state
        self.__timer = threading.Timer(self.__blink_interval,
                                       self.blink_start)
        self.__duty = LedControler.__DEFAULT_PWM_DUTY
        self.__start_flag = False

        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(pin, gpio.OUT)
        self.__pwm = gpio.PWM(pin, 1000)

    def on(self):
        self.blink_stop()
        print('duty =',self.__duty)
        print('interval =',self.__blink_interval)
        self.__pwm.start(float(self.__duty))
        self.__pin_state = 1

    def off(self):
        self.blink_stop()
        self.__pwm.stop()
        self.__pin_state = 0


    def blink_start(self):
        if self.__start_flag:
            return

        self.__blink_core()
        self.__start_flag = True

    def __blink_core(self):
        self.__toggle()
        self.__timer = threading.Timer(self.__blink_interval,
                                       self.__blink_core)
        self.__timer.start()

    def blink_stop(self):
        self.__timer.cancel()
        self.__pwm.stop()
        self.__start_flag = False


    def set_blink_interval(self, interval):
        if interval == 0:
            print('invalid led blink interval')
            return

        self.__blink_interval = interval

    def set_pwm_duty(self, duty):
        self.__duty = duty

    def __toggle(self):
        self.__pin_state = ~self.__pin_state & 0x01

        if self.__pin_state:
            self.__pwm.start(float(self.__duty))
        else:
            self.__pwm.stop()


if __name__ == '__main__':
    led = LedControler(14,1) #fixme set args
    led.set_pwm_duty(50)
    led.set_blink_interval(2)
    led.blink_start()
    while(True):
        pass
