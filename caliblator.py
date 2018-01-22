# -*- coding: utf-8 -*-

import Cv2ImgRotator
import sys
import csv
import cv2
import util

class Caliblator(object):
    def __init__(self, img):
        self.__rotator = Cv2ImgRotator.Cv2ImgRotator(img.copy())
        self.__img = self.__rotator.getResizeImg()
        self.__center = {"x":int(self.__img.shape[1]/2), "y":int(self.__img.shape[0]/2)}
        self.__center_tupple = (self.__center["x"], self.__center["y"])
        self.__img_size = {"width":self.__img.shape[1], "height":self.__img.shape[0]}
        self.__img_size_tupple = (self.__img.shape[1], self.__img.shape[0])
        self.__calib_data = util.readConfig()
        self.__line_y = 0
        #debug
#        cv2.imshow("img", self.__img)
#        cv2.waitKey(0)
        
        # cv2.imshow("test", self.__img_rot)
        # cv2.waitKey(0)

    def __getCurrentConfigImg(self):
        print('angle calib =', self.__calib_data['angle'])
        ret_img = self.__rotator.rotateAuto(self.__calib_data["angle"])
        color = (0,0,255)
        line_width = 1
        line_ypos = self.__center["y"] - self.__calib_data["level"]

        cv2.line(ret_img,
                 (0, line_ypos),
                 (self.__img_size["width"] - 1, line_ypos),
                 color,
                 line_width)

        #debug
#        cv2.imshow("current_config_img", ret_img)
#        cv2.waitKey(0)

        return ret_img


    def __reRotate(self):
        self.__calib_data["angle"] = self.__rotator.rotateInteractive()

    def __mouseCallback(self, eventType, x, y, flags, userdata):
        if eventType == cv2.EVENT_LBUTTONDOWN:
#            self.__line_y = self.__center["y"] - y
            self.__calib_data["level"] = self.__center["y"] - y

    def __reSetLevel(self):
        current_img = self.__getCurrentConfigImg()
        window_name = "re_set_img!"
        cv2.imshow(window_name, current_img)
        cv2.setMouseCallback(window_name, self.__mouseCallback, None)

        while True:
            current_img = self.__getCurrentConfigImg()
            cv2.imshow(window_name, current_img)
            if cv2.waitKey(30) == 27:
                cv2.destroyWindow(window_name)
                break

    def __putText(self, img):
        start_pos1 = (10, int(self.__img_size["height"]*6/8))
        start_pos2 = (10,int(self.__img_size["height"]*7/8))
        font_type = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 0.5
        color = (0,255,127)
        font_bold = 1
        line_type = cv2.LINE_AA

        cv2.putText(img,
                    "r: Rotate",
                    start_pos1,
                    font_type,
                    font_size,
                    color,
                    font_bold,
                    line_type)

        cv2.putText(img,
                    "l: Level",
                    start_pos2,
                    font_type,
                    font_size,
                    color,
                    font_bold,
                    line_type)


        return img

    def __saveConfig(self):
        write_array = [["angle", self.__calib_data["angle"]],
                       ["level", self.__calib_data["level"]]]
        
        with open('config.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(write_array)

    def chooseMode(self):
        window_name = "chose_mode!"

        while True:
            current_img = self.__getCurrentConfigImg()
            cv2.imshow(window_name, self.__putText(current_img))

            key = cv2.waitKey(0)
            cv2.destroyWindow(window_name)

            if key == 114: # r
                self.__reRotate()
            elif key == 108: # l
                self.__reSetLevel()
            elif key == 27: #ESC
                break

        self.__saveConfig()



if __name__ == '__main__':
    args = sys.argv
    if len(args) <= 1:
        print ('please input image name')
        sys.exit()

    img = cv2.imread(args[1])
    if img is None:
        print ('no image!!:', img_name)
        sys.exit()


    caliblator = Caliblator(img)
    caliblator.chooseMode()
