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
    __AUDIO = audio_player.AudioPlayerPygame(__AUDIO_NAME)
    __CAPTURE = cv2.VideoCapture(0)
    __DETECTOR = detector.Detector(__COLOR_VECT, __VECT_LEN_TH)


    def __init__(self):
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
        self.__CAPTURE.set(3,320)
        self.__CAPTURE.set(4,240)
        if not self.__CAPTURE:
            print("Could not open camera")
            sys.exit()


    def __push_event(self, event_key):
        print('pushed event:', event_key)
        if event_key not in self.__EVENT_KIND:
            print('[push_event error] no such event:', event_key)
            return self.__RET_FAIL

        self.__event_buf.append(event_key)
        return self.__RET_SUCCESS

    def __null_proc(self):
        pass

    def __switch_proc_sleeping(self):
        self.__state_key = 'detecting'
        timer = threading.Timer(self.__DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()

    def __switch_proc_detecting_indicating(self):
        self.__state_key = 'sleeping'
        self.__AUDIO.stop()

    def __timer_proc(self):
        _, img = self.__CAPTURE.read()
        self.__DETECTOR.input_img(img)

        if self.__DETECTOR.detect():
            self.__push_event('detected_full')
            print('detected full!!')
            self.__DETECTOR.showResult()

        else:
            self.__push_event('detected_not_full')

    def __detected_full_proc(self):
        self.__state_key = 'indicating'
        self.__AUDIO.play(loop=True)

    def __detected_not_full_proc(self):
        timer = threading.Timer(self.__DETECT_FREQ_SEC,
                                self.__push_event,
                                args=['timer'])

        timer.start()


    def __proc(self, event_key):
        if event_key not in self.__EVENT_KIND:
            return self.__RET_FAIL

        self.__procs[self.__STATE_KIND[self.__state_key]][self.__EVENT_KIND[event_key]]()

        return self.__RET_SUCCESS

    def __debug_print_state_loop(self):
        print('state:', self.__state_key)
        print('event_num:', len(self.__event_buf))

        timer_debug = threading.Timer(self.__DEBUG_TIMER_FREQ_SEC,
                                      self.__debug_print_state_loop)
        timer_debug.start()

    def start_wait_event_loop(self):
        timer_debug = threading.Timer(self.__DEBUG_TIMER_FREQ_SEC,
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
