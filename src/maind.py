#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
from distutils.util import strtobool
import threading
import sys
import configparser
import cv2  ##only for keybord debug
import numpy as np
import audio_player
from line_laser_detector import LineLaserDetector
import switch_ctrl as sw
import led_ctrl
import RPi.GPIO as gpio
import subprocess

class StateMachine(object):
    __EVENT_KIND = {'switch':0,
                    'timer':1,
                    'detected_full':2,
                    'detected_not_full':3,
                    'detected_light_on':4,
                    'detected_light_off':5}
    __STATE_KIND = {'sleeping':0, 'light_detecting':1, 'laser_detecting':2, 'indicating':3}
    __RET_SUCCESS = True
    __RET_FAIL = False
    __LIGHT_DETECT_FREQ_SEC = 5
    __LASER_DETECT_FREQ_SEC = 10
    __COLOR_VECT = np.array([0,0,1])
    __VECT_LEN_TH = 0.8
    __DEBUG_TIMER_FREQ_SEC = 0.2
    __PATH_BASE = os.path.dirname(os.path.abspath(__file__))
    __AUDIO_NAME_FULL = os.path.normpath(os.path.join(__PATH_BASE, '../sound/meron_large_16db.wav'))
    __AUDIO_NAME_LIGHT_ON = os.path.normpath(os.path.join(__PATH_BASE, '../sound/lamp-oshizu_large_16db.wav'))
    __SAVE_IMG_PATH =  os.path.normpath(os.path.join(__PATH_BASE, '../debug/output_img'))
    __SW_PIN_NUM = 20
    __LED_PIN_NUM = 14
    __LASER_PIN = 16

    def __init__(self, detector):
        subprocess.call(['v4l2-ctl', '--set-ctrl=brightness=10'])  # set camera brightness
        subprocess.call(['amixer', 'sset', 'PCM', '100%'])  # set camera brightness        
        self.__audio = audio_player.AudioPlayerPygame()
        self.__capture = cv2.VideoCapture(0)
        self.__detector = detector

        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(StateMachine.__PATH_BASE, './config'), 'UTF-8')

        self.__mac_debug = strtobool(self.__config.get('debug', 'mac_debug'))
        self.__pi_debug = strtobool(self.__config.get('debug', 'pi_debug'))

        if not self.__mac_debug:
            sw.sw_set_callback(StateMachine.__SW_PIN_NUM, (lambda pin: self.__push_event('switch')))
            self.__led = led_ctrl.LedControler(StateMachine.__LED_PIN_NUM, 1)
            self.__led_interval_sleeping = float(self.__config.get('led', 'interval_sleeping'))
            self.__led_interval_detecting = float(self.__config.get('led', 'interval_detecting'))
#            self.__led.set_blink_interval(self.__led_interval_sleeping)
#            self.__led.set_pwm_duty(self.__config.get('led', 'pwm_duty'))
#            self.__led.blink_start()
            self.__led.set_pwm_freq(1.0/self.__led_interval_sleeping)
            self.__led.on()
            gpio.setwarnings(False)
            gpio.setmode(gpio.BCM)
            gpio.setup(StateMachine.__LASER_PIN, gpio.OUT)
            gpio.output(StateMachine.__LASER_PIN, gpio.LOW)

            print('gpio and led init end!')

        self.__state_key = 'sleeping'
        self.__sleeping_proc = (self.__switch_proc_sleeping,
                                self.__null_proc,
                                self.__null_proc,
                                self.__null_proc,
                                self.__null_proc,
                                self.__null_proc)

        self.__light_detecting_proc = (self.__switch_proc_detecting_indicating,
                                       self.__timer_proc_light_detecting,
                                       self.__detected_full_proc,
                                       self.__detected_not_full_proc,
                                       self.__detected_light_on_proc,
                                       self.__detected_light_off_proc)

        self.__laser_detecting_proc = (self.__switch_proc_detecting_indicating,
                                       self.__timer_proc_laser_detecting,
                                       self.__detected_full_proc,
                                       self.__detected_not_full_proc,
                                       self.__detected_light_on_proc,
                                       self.__null_proc)

        self.__indicating_proc = (self.__switch_proc_detecting_indicating,
                                  self.__null_proc,
                                  self.__null_proc,
                                  self.__null_proc,
                                  self.__null_proc,
                                  self.__null_proc)

        self.__procs = (self.__sleeping_proc,
                        self.__light_detecting_proc,
                        self.__laser_detecting_proc,
                        self.__indicating_proc)

        self.__event_buf = []
        self.__capture.set(3,320)
        self.__capture.set(4,240)
        if not self.__capture:
            print("Could not open camera")
            sys.exit()

        self.__timer_count = 0

        print('init end!')
    @classmethod
    def __laser_on(cls):
        gpio.output(cls.__LASER_PIN, gpio.HIGH)

    @classmethod
    def __laser_off(cls):
        gpio.output(cls.__LASER_PIN, gpio.LOW)


    def __push_event(self, event_key):
        if self.__mac_debug  or self.__pi_debug:
            print('pushed event:', event_key)
        if event_key not in StateMachine.__EVENT_KIND:
            print('[push_event error] no such event:', event_key)
            return self.__RET_FAIL

        self.__event_buf.append(event_key)
        return StateMachine.__RET_SUCCESS

    def __null_proc(self):
        pass

    def __switch_proc_sleeping(self):
        self.__state_key = 'light_detecting'
        if not self.__mac_debug:
            #self.__led.set_blink_interval(self.__led_interval_detecting)
            self.__led.set_pwm_freq(1.0/self.__led_interval_detecting)
            self.__led.on()
        timer = threading.Timer(StateMachine.__LIGHT_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()

    def __switch_proc_detecting_indicating(self):
        self.__state_key = 'sleeping'
        if not self.__mac_debug:
#            self.__led.set_blink_interval(self.__led_interval_sleeping)
            self.__led.set_pwm_freq(1.0/self.__led_interval_sleeping)
            self.__led.on()

            self.__laser_off()

        self.__audio.stop()


    def __timer_proc_light_detecting(self):
        for i in range(2): ## kara capture
            self.__capture.read()
            time.sleep(0.1)

        _, img = self.__capture.read()
        self.__detector.input_img(img)
        result = self.__detector.detect(mode='on_off')

        if result == LineLaserDetector.RESULT_INVALID_ENV:
            self.__push_event('detected_light_on')
        else:
            self.__push_event('detected_light_off')

    def __timer_proc_laser_detecting(self):
        self.__timer_count += 1 #for debug

        for i in range(2): ## kara capture
            self.__capture.read()
            time.sleep(0.1)

        _, img = self.__capture.read()
        self.__detector.input_img(img)
        result = self.__detector.detect()

        if result == LineLaserDetector.RESULT_NOT_FULL:
            if self.__pi_debug:
                tmp_path = os.path.normpath(os.path.join(StateMachine.__PATH_BASE, '../debug/output_img/result_not_full'))                
                cv2.imwrite(tmp_path + str(self.__timer_count) + '.png',
                            self.__detector.get_calib_img())
            self.__push_event('detected_not_full')

        elif result == LineLaserDetector.RESULT_FULL:
            if self.__pi_debug:
                tmp_path = os.path.normpath(os.path.join(StateMachine.__PATH_BASE, '../debug/output_img/result_full'))

                cv2.imwrite(tmp_path + str(self.__timer_count) + '.png',
                            self.__detector.get_calib_img())
            self.__push_event('detected_full')

        elif result == LineLaserDetector.RESULT_INVALID_ENV:
            self.__push_event('detected_light_on')

        else:
            self.__push_event('detected_not_full')  ##fixme

        ########### for debug ################
        # save_img = self.__detector.detect()
        # cv2.imwrite(StateMachine.__SAVE_IMG_PATH
        #             + '/capture_img'
        #             + str(self.__timer_count)
        #             + '.png'
        #             ,save_img)

#        self.__push_event('detected_not_full')
    def __detected_light_on_proc(self):
        self.__state_key = 'light_detecting'
        if not self.__mac_debug:
            self.__laser_off()

        self.__audio.set_music(StateMachine.__AUDIO_NAME_LIGHT_ON)
        self.__audio.play(loop=True)
        timer = threading.Timer(StateMachine.__LIGHT_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __detected_light_off_proc(self):
        self.__state_key = 'laser_detecting'
        if not self.__mac_debug:
            self.__laser_on()

        self.__audio.set_music(StateMachine.__AUDIO_NAME_LIGHT_ON)
        self.__audio.stop()
        timer = threading.Timer(StateMachine.__LASER_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __detected_full_proc(self):
        self.__state_key = 'indicating'
        if not self.__mac_debug:
            self.__laser_off()

        self.__audio.set_music(StateMachine.__AUDIO_NAME_FULL)
        self.__audio.play(loop=True)

    def __detected_not_full_proc(self):
        timer = threading.Timer(StateMachine.__LASER_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __proc(self, event_key):
        if event_key not in StateMachine.__EVENT_KIND:
            return StateMachine.__RET_FAIL

        self.__procs[StateMachine.__STATE_KIND[self.__state_key]][StateMachine.__EVENT_KIND[event_key]]()

        return StateMachine.__RET_SUCCESS

    def __debug_print_state_loop(self):
        print('state:', self.__state_key)
        print('event_num:', len(self.__event_buf))

        timer_debug = threading.Timer(StateMachine.__DEBUG_TIMER_FREQ_SEC,
                                      self.__debug_print_state_loop)
        timer_debug.start()

    def start_wait_event_loop(self):
        if self.__mac_debug:
            img = cv2.imread('button.png')#only for debug

        if self.__mac_debug is True or self.__pi_debug is True:
            timer_debug = threading.Timer(StateMachine.__DEBUG_TIMER_FREQ_SEC,
                                          self.__debug_print_state_loop)

            timer_debug.start()


        while True:
            #switch debug
            if self.__mac_debug:
                cv2.imshow("switch", img)
                if cv2.waitKey(1) == 115:  #'s'
                    print('switch pushed!')
                    self.__push_event('switch')

            if self.__event_buf:
                event_key = self.__event_buf[0]
                if self.__mac_debug or self.__pi_debug:
                    print('event:', event_key)
                    print('status:', self.__state_key)
                del self.__event_buf[0]

                self.__proc(event_key)


def fork():
    pid = os.fork()
    
    if pid > 0:
        f = open('/var/run/BathWaterLevel.pid','w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()

    if pid == 0:
        print('Bath Water Level Detection Service start!')
        detector = LineLaserDetector()
        state_machine = StateMachine(detector)

        state_machine.start_wait_event_loop()

if __name__ == '__main__':
    fork()
#    print('Bath Water Level Detection Service start!')
#    detector = LineLaserDetector()
#    state_machine = StateMachine(detector)
#    state_machine.start_wait_event_loop()
    
