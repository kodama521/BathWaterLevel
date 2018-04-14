# -*- coding: utf-8 -*-

from line_laser_detector import LineLaserDetector
import threading
import numpy as np
import sys
import cv2  ##only for keybord debug
import audio_player
import configparser


mac_debug = True
pi_debug = False

if not mac_debug:
    import switch_ctrl as sw

COLOR_VECT = np.array([0,0,1])
VECT_LEN_TH = 0.8
LEVEL_TH = 100


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
    __AUDIO_NAME_FULL = '../sound/lamp-oshizu.wav'
    __AUDIO_NAME_LIGHT_ON = '../sound/tanuki.wav'
    __SAVE_IMG_PATH = '../debug/output_img'
    __SW_PIN_NUM = 20

    def __init__(self, detector):
        self.__audio = audio_player.AudioPlayerPygame()
        self.__capture = cv2.VideoCapture(0)
        self.__detector = detector

        config = configparser.ConfigParser()
        config.read('./config', 'UTF-8')

        self.__mac_debug = config.get('debug', 'mac_debug')
        self.__pi_debug = config.get('debug', 'pi_debug')


        if not self.__mac_debug:
            sw.sw_set_callback(StateMachine.__SW_PIN_NUM, (lambda pin: self.__push_event('switch')))

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

    def __push_event(self, event_key):
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
        timer = threading.Timer(StateMachine.__LIGHT_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()

    def __switch_proc_detecting_indicating(self):
        self.__state_key = 'sleeping'
        self.__audio.stop()


    def __timer_proc_light_detecting(self):
        _, img = self.__capture.read()
        self.__detector.input_img(img)
        result = self.__detector.detect()

        if result == LineLaserDetector.RESULT_INVALID_ENV:
            self.__push_event('detected_light_on')
        else:
            self.__push_event('detected_light_off')

    def __timer_proc_laser_detecting(self):
        self.__timer_count += 1 #for debug

        _, img = self.__capture.read()
        self.__detector.input_img(img)
        result = self.__detector.detect()

        if result == LineLaserDetector.RESULT_NOT_FULL:
            self.__push_event('detected_not_full')

        elif result == LineLaserDetector.RESULT_FULL:
            cv2.imwrite('../debug/output_img/result.png', img)
            self.__push_event('detected_full')

        elif result == LineLaserDetector.RESULT_INVALID_ENV:
            self.__push_event('detected_light_on')

##        else:
##            self.__push_event('detected_not_full')

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
        self.__audio.set_music(StateMachine.__AUDIO_NAME_LIGHT_ON)
        self.__audio.play(loop=True)
        timer = threading.Timer(StateMachine.__LIGHT_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __detected_light_off_proc(self):
        self.__state_key = 'laser_detecting'
        self.__audio.set_music(StateMachine.__AUDIO_NAME_LIGHT_ON)
        self.__audio.play(loop=True)
        timer = threading.Timer(StateMachine.__LASER_DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __detected_full_proc(self):
        self.__state_key = 'indicating'
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
            timer_debug = threading.Timer(StateMachine.__DEBUG_TIMER_FREQ_SEC,
                                          self.__debug_print_state_loop)

            timer_debug.start()

            img = cv2.imread('button.png')#only for debug

        while True:
            #switch debug
            cv2.imshow("switch", img)
            if cv2.waitKey(1) == 115:  #'s'
                print('switch pushed!')
                self.__push_event('switch')

            if self.__event_buf:
                event_key = self.__event_buf[0]
                print('event:', event_key)
                del self.__event_buf[0]

                self.__proc(event_key)



if __name__ == '__main__':
    detector = LineLaserDetector()
    state_machine = StateMachine(detector)
    state_machine.start_wait_event_loop()
