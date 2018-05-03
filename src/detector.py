# -*- coding: utf-8 -*-

import cv2
import Cv2ImgRotator
import util
import numpy as np

import sys #debug

import clientimg

class Detector(object):
    _BLK_SIZE = 10
    _PIX_INTENSITY_TH = 100
    _IMG_SIZE =(320 ,240)

    RESULT_ERROR = -1

    RESULT_NOT_FULL = 0
    RESULT_FULL = 1
    RESULT_INVALID_ENV = 2
    RESULT_VALID_ENV = 3

    
    def __init__(self):
        self._calib_data = util.readCalibFile()
        #not initialized param
        self._rotator = Cv2ImgRotator.Cv2ImgRotator()
        self._img_rotate = None
        self._img_size = {"x":0, "y":0}
        self._center = {"x":0, "y":0}
        self._center_tupple = {"x":0, "y":0}
        self._img_result = None
        self._inited = False

    def input_img(self, img):
        self._img_resize = cv2.resize(img, Detector._IMG_SIZE)
        self._rotator.input_img(self._img_resize)
        self._img_rotate = self._rotator.rotateAuto(self._calib_data['angle'][0])
        self._img_size = {"x":int(self._img_rotate.shape[1]),
                          "y":int(self._img_rotate.shape[0])}

        self._center = {"x":int(self._img_rotate.shape[1]/2),
                         "y":int(self._img_rotate.shape[0]/2)}
        self._center_tupple = (self._center["x"], self._center["y"])
        #debug
        self._img_result = self._img_rotate.copy()
        self._inited = True

    def get_calib_img(self):
        return self._img_rotate

if __name__ == '__main__':
    @staticmethod
    def _get_mean_pixel(img, x_range, y_range):
        bgr_vect_sum = np.array([0,0,0])
        for y in y_range:
            for x in x_range:
                bgr_vect_sum += np.array(img[y,x])

        return bgr_vect_sum / (len(x_range) * len(y_range))

    def _get_level(self, y):
        return self._center['y'] - y

    def detect(self, color_vect, vect_len_th):
        color_vect_uni = color_vect / np.linalg.norm(color_vect)

        if not self._inited:
            print('input image!!')
            return False

        x_size = self._img_size['x']
        y_size = self._img_size['y']
#        _, level = util.transPosOriginal(y=self._calib_data["level"][0],
#                                         center_y=self._center["y"])
        
        start_x, start_y = util.transPosOriginal(x=self._calib_data["area"][0],
                                                 y=self._calib_data["area"][3],
                                                 center_x=self._center["x"],
                                                 center_y=self._center["y"])

        end_x, end_y = util.transPosOriginal(x=self._calib_data["area"][2],
                                             y=self._calib_data["level"][0],
                                             center_x=self._center["x"],
                                             center_y=self._center["y"])
        end_x -= Detector._BLK_SIZE
        end_y -= Detector._BLK_SIZE
#        print(start_x, start_y)
#        print(end_x, end_y)
#        print(Detector._BLK_SIZE)

        for y in range(start_y, end_y, Detector._BLK_SIZE):
            for x in range(start_x, end_x, Detector._BLK_SIZE):
                pix_val = self._get_mean_pixel(self._img_rotate, range(x,x+Detector._BLK_SIZE), range(y,y+Detector._BLK_SIZE))
                if np.linalg.norm(pix_val) > Detector._PIX_INTENSITY_TH:
                    pix_val /= np.linalg.norm(pix_val)
                else:
                    pix_val *= 0
                if np.dot(color_vect_uni, pix_val) >= vect_len_th:
                    self._img_result[y:y+Detector._BLK_SIZE, x:x+Detector._BLK_SIZE] = (255,0,0)
#                    if y > self._calib_data["level"][0] - Detector._BLK_SIZE:
                    return True

        return False

    def showResult(self):
        tmp_img = self._img_result.copy()

        color = (0,0,255)
        line_width = 1

        _, line_ypos = util.transPosOriginal(y=self._calib_data["level"][0],
                                             center_y=self._center["y"])
        cv2.line(tmp_img,
                 (0, line_ypos),
                 (self._img_size["x"] - 1, line_ypos),
                 color,
                 line_width)


        rect_pos_left_upper = util.transPosOriginal(x=self._calib_data["area"][0],
                                                    y=self._calib_data["area"][3],
                                                    center_x=self._center["x"],
                                                    center_y=self._center["y"])

        rect_pos_right_lower = util.transPosOriginal(x=self._calib_data["area"][2],
                                                     y=self._calib_data["area"][1],
                                                     center_x=self._center["x"],
                                                     center_y=self._center["y"])
        
        
        cv2.rectangle(tmp_img,
                      tuple(rect_pos_left_upper),
                      tuple(rect_pos_right_lower),
                      (0, 255, 0),
                      line_width)

        cv2.imshow("result", tmp_img)
        cv2.waitKey(0)

if __name__ == '__main__':
    DEFAULT_IMG = '../test_img/test.jpg'
    COLOR_VECT = np.array([0,135,107])
    VECT_LEN_TH = 0.9
    
#    args = sys.argv
#    if len(args) <= 1:
#        img_name = DEFAULT_IMG
#    else:
#        img_name = args[1]
    
    img = cv2.imread(DEFAULT_IMG)
    #カメラの設定
#    capture=cv2.VideoCapture(0)
#    capture.set(3,320)
#    capture.set(4,240)
    # if not capture:
    #     print("Could not open camera")
    #     sys.exit()

    # _, img=capture.read()

#    if img is None:
#        print ('no image!!:', img_name)
#        sys.exit()

    detector = Detector()
    detector.input_img(img)
    print("result = ", detector.detect(COLOR_VECT, VECT_LEN_TH))
    detector.showResult()

