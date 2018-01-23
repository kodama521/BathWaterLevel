# -*- coding: utf-8 -*-

import cv2
import Cv2ImgRotator
import util
import numpy as np

import sys #debug

class Detector(object):
    BLK_SIZE = 3

    def __init__(self, img, level_th, color_vect, vect_len_th):
        self.__level_th = level_th
        self.__vect_len_th = vect_len_th
        self.__color_vect_uni = color_vect / np.linalg.norm(color_vect)
        self.__rotator = Cv2ImgRotator.Cv2ImgRotator(img.copy())
        self.__calib_data = util.readConfig()
        self.__img_rotate = self.__rotator.rotateAuto(self.__calib_data['angle'])
        self.__img_size = {"x":int(self.__img_rotate.shape[1]),
                           "y":int(self.__img_rotate.shape[0])}

        self.__center = {"x":int(self.__img_rotate.shape[1]/2),
                         "y":int(self.__img_rotate.shape[0]/2)}
        self.__center_tupple = (self.__center["x"], self.__center["y"])
        #debug
        self.__img_result = self.__img_rotate.copy()

                
    @staticmethod
    def __get_mean_pixel(img, x_range, y_range):
        bgr_vect_sum = np.array([0,0,0])
        for y in y_range:
            for x in x_range:
                bgr_vect_sum += np.array(img[x,y])

        return bgr_vect_sum / (len(x_range) * len(y_range))

    
    def detect_range(self):
        x_size = self.__img_size['x']
        y_size = self.__img_size['y']
        
        for y in range(0, self.__img_size['y']-self.BLK_SIZE, self.BLK_SIZE):
            for x in range(0, self.__img_size['x']-self.BLK_SIZE, self.BLK_SIZE):
                pix_val = self.__get_mean_pixel(self.__img_rotate, range(x,x+self.BLK_SIZE), range(y,y+self.BLK_SIZE))
                if np.linalg.norm(pix_val) > 0:
                    pix_val /= np.linalg.norm(pix_val)
                else:
                    pix_val *= 0
                if np.dot(self.__color_vect_uni, pix_val) >= self.__vect_len_th:
                    self.__img_result[x:x+self.BLK_SIZE, y:y+self.BLK_SIZE] = (0,255,0)

        
        cv2.imshow("result", self.__img_result)
        cv2.waitKey(0)

if __name__ == '__main__':
    DEFAULT_IMG = 'test.jpg'
    COLOR_VECT = np.array([0,0,1])
    VECT_LEN_TH = 0.8
    LEVEL_TH = 100
    
    args = sys.argv
    if len(args) <= 1:
        img_name = DEFAULT_IMG
    else:
        img_name = args[1]
    
    img = cv2.imread(img_name)
    if img is None:
        print ('no image!!:', img_name)
        sys.exit()

    detector = Detector(img, LEVEL_TH, COLOR_VECT, VECT_LEN_TH)
    detector.detect_range()
