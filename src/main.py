# -*- coding: utf-8 -*-

import detector
import threading
import numpy as np
import sys
import cv2  ##only for keybord debug
import audio_player

COLOR_VECT = np.array([0,0,1])
VECT_LEN_TH = 0.8
LEVEL_TH = 100


class StateMachine(object):
    __EVENT_KIND = {'switch':0, 'timer':1, 'detected_full':2, 'detected_not_full':3}
    __STATE_KIND = {'sleeping':0, 'detecting':1, 'indicating':2}
    __RET_SUCCESS = True
    __RET_FAIL = False
    __DETECT_FREQ_SEC = 10
    __COLOR_VECT = np.array([0,0,1])
    __VECT_LEN_TH = 0.8
    __DEBUG_TIMER_FREQ_SEC = 0.2
    __AUDIO_NAME = 'tanuki.wav'

    def __init__(self):
        self.__audio = audio_player.AudioPlayerPygame(StateMachine.__AUDIO_NAME)
        self.__capture = cv2.VideoCapture(0)
        self.__detector = detector.Detector(StateMachine.__COLOR_VECT,
                                            StateMachine.__VECT_LEN_TH)

        self.__state_key = 'sleeping'
        self.__sleeping_proc = (self.__switch_proc_sleeping,
                                self.__null_proc,
                                self.__null_proc,
                                self.__null_proc)

        self.__detecting_proc = (self.__switch_proc_detecting_indicating,
                                 self.__timer_proc,
                                 self.__detected_full_proc,
                                 self.__detected_not_full_proc
                                 )

        self.__indicating_proc = (self.__switch_proc_detecting_indicating,
                                  self.__null_proc,
                                  self.__null_proc,
                                  self.__null_proc)

        self.__procs = (self.__sleeping_proc,
                        self.__detecting_proc,
                        self.__indicating_proc)

        self.__event_buf = []
        self.__capture.set(3,320)
        self.__capture.set(4,240)
        if not self.__capture:
            print("Could not open camera")
            sys.exit()


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
        self.__state_key = 'detecting'
        timer = threading.Timer(StateMachine.__DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()

    def __switch_proc_detecting_indicating(self):
        self.__state_key = 'sleeping'
        self.__audio.stop()

    def __timer_proc(self):
        _, img = self.__capture.read()
        self.__detector.input_img(img)

        if self.__detector.detect():
            self.__push_event('detected_full')
            print('detected full!!')
            self.__detector.showResult()

        else:
            self.__push_event('detected_not_full')

    def __detected_full_proc(self):
        self.__state_key = 'indicating'
        self.__audio.play(loop=True)

    def __detected_not_full_proc(self):
        timer = threading.Timer(StateMachine.__DETECT_FREQ_SEC,
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
    state_machine = StateMachine()
    state_machine.start_wait_event_loop()
