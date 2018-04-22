import RPi.GPIO as gpio

def sw_set_callback(pin, callback, event_type=gpio.FALLING):
    gpio.setmode(gpio.BCM)
    gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(pin, event_type, callback=callback, bouncetime=200)


def debug_callback(pin):
    print('no.',pin)
    print('pin is pushed!')

if __name__ == '__main__':
#    sw_set_callback(20, debug_callback)
    sw_set_callback(20, (lambda pin: debug_callback(pin)))
        
    while True:
        pass
