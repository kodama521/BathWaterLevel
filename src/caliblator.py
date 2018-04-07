# -*- coding: utf-8 -*-

import Cv2ImgRotator
import sys
import csv
import cv2
import util

class Caliblator(object):
    __IMG_SIZE =(320 ,240)

    def __init__(self, img):
        self.__rotator = Cv2ImgRotator.Cv2ImgRotator()
        self.__rotator.input_img(cv2.resize(img, Caliblator.__IMG_SIZE))
        self.__img = self.__rotator.getResizeImg()
        self.__center = {"x":int(self.__img.shape[1]/2), "y":int(self.__img.shape[0]/2)}
        self.__center_tupple = (self.__center["x"], self.__center["y"])
        self.__img_size = {"width":self.__img.shape[1], "height":self.__img.shape[0]}
        self.__img_size_tupple = (self.__img.shape[1], self.__img.shape[0])
        self.__line_y = 0
        self.__calib_data = util.readConfig()
        self.__setting_area = False

        #debug
#        cv2.imshow("img", self.__img)
#        cv2.waitKey(0)
        
        # cv2.imshow("test", self.__img_rot)
        # cv2.waitKey(0)

    def __getCurrentConfigImg(self):
#        print('angle calib =', self.__calib_data['angle'][0])
        ret_img = self.__rotator.rotateAuto(self.__calib_data["angle"][0])
        color = (0,0,255)
        line_width = 1
        _, line_ypos = util.transPosOriginal(y=self.__calib_data["level"][0],
                                             center_y=self.__center["y"])

        cv2.line(ret_img,
                 (0, line_ypos),
                 (self.__img_size["width"] - 1, line_ypos),
                 color,
                 line_width)


        rect_pos_left_upper = util.transPosOriginal(x=self.__calib_data["area"][0],
                                                    y=self.__calib_data["area"][3],
                                                    center_x=self.__center["x"],
                                                    center_y=self.__center["y"])

        rect_pos_right_lower = util.transPosOriginal(x=self.__calib_data["area"][2],
                                                       y=self.__calib_data["area"][1],
                                                       center_x=self.__center["x"],
                                                       center_y=self.__center["y"])
        
        
        cv2.rectangle(ret_img,
                      tuple(rect_pos_left_upper),
                      tuple(rect_pos_right_lower),
                      (0, 255, 0),
                      line_width)

#        print('rect_pos =', (self.__calib_data["area"][0] + self.__center["x"], self.__center["y"] - self.__calib_data["area"][1]),
 #                     (self.__calib_data["area"][2] + self.__center["x"], self.__center["y"] - self.__calib_data["area"][3]))
        #debug
#        cv2.imshow("current_config_img", ret_img)
#        cv2.waitKey(0)

        return ret_img


    def __reRotate(self):
        self.__calib_data["angle"][0] = self.__rotator.rotateInteractive()

    def __mouseCallbackLevel(self, eventType, x, y, flags, userdata):
        if eventType == cv2.EVENT_LBUTTONDOWN:
#            self.__line_y = self.__center["y"] - y
            self.__calib_data["level"][0] = self.__center["y"] - y

    def __reSetLevel(self):
        current_img = self.__getCurrentConfigImg()
        window_name = "re_set_level!"
        cv2.imshow(window_name, current_img)
        cv2.setMouseCallback(window_name, self.__mouseCallbackLevel, None)

        self.__showCurrentConfigImgLoop(window_name)
        
    def __mouseCallbackArea(self, eventType, x, y, flags, userdata):
        if eventType == cv2.EVENT_LBUTTONDOWN:
            self.__setting_area = True

            (self.__calib_data["area"][0],
             self.__calib_data["area"][1]) = util.transPosCenterBase(x=x,
                                                                     y=y,
                                                                     center_x=self.__center["x"],
                                                                     center_y=self.__center["y"])
            (self.__calib_data["area"][2],
             self.__calib_data["area"][3]) = (self.__calib_data["area"][0],
                                              self.__calib_data["area"][1])


        elif eventType == cv2.EVENT_MOUSEMOVE:
            if self.__setting_area:
                (self.__calib_data["area"][2],
                 self.__calib_data["area"][3]) = util.transPosCenterBase(x=x,
                                                                         y=y,
                                                                         center_x=self.__center["x"],
                                                                         center_y=self.__center["y"])

        elif eventType == cv2.EVENT_LBUTTONUP:
            self.__setting_area = False
            tmp_x = self.__calib_data["area"][0]
            tmp_y = self.__calib_data["area"][1]

            self.__calib_data["area"][0] = min(tmp_x, self.__calib_data["area"][2])
            self.__calib_data["area"][1] = min(tmp_y, self.__calib_data["area"][3])
            self.__calib_data["area"][2] = max(tmp_x, self.__calib_data["area"][2])
            self.__calib_data["area"][3] = max(tmp_y, self.__calib_data["area"][3])
            

    def __reSetArea(self):
        current_img = self.__getCurrentConfigImg()
        window_name = "re_set_area!"
        cv2.imshow(window_name, current_img)
        cv2.setMouseCallback(window_name, self.__mouseCallbackArea, None)
        self.__showCurrentConfigImgLoop(window_name)


    def __showCurrentConfigImgLoop(self, window_name):
        while True:
            current_img = self.__getCurrentConfigImg()
            cv2.imshow(window_name, current_img)
            if cv2.waitKey(30) == 27:
                cv2.destroyWindow(window_name)
                break

        
    def __putText(self, img):
        start_pos1 = (10, int(self.__img_size["height"]*5/8))
        start_pos2 = (10,int(self.__img_size["height"]*6/8))
        start_pos3 = (10,int(self.__img_size["height"]*7/8))
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

        cv2.putText(img,
                    "a: Area",
                    start_pos3,
                    font_type,
                    font_size,
                    color,
                    font_bold,
                    line_type)


        return img

    def __saveConfig(self, path):
        write_array = [["angle", self.__calib_data["angle"][0]],
                       ["level", self.__calib_data["level"][0]],
                       ["area",
                        self.__calib_data["area"][0],
                        self.__calib_data["area"][1],
                        self.__calib_data["area"][2],
                        self.__calib_data["area"][3]]]
        
        with open(path + 'config.csv', 'w') as f:
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
            elif key == 97: # a
                self.__reSetArea()
#            elif key == 27: #ESC
#                break

            self.__saveConfig('../')



if __name__ == '__main__':
    args = sys.argv
    IMG_NAME_DEFAULT = '../test_img/IMG_7645.JPG'
    img_name = IMG_NAME_DEFAULT
    if len(args) <= 1:
        print ('img set default', IMG_NAME_DEFAULT)
    else:
        img_name = args[1]


    img = cv2.imread(img_name)
    if img is None:
        print ('no image!!:', img_name)
        sys.exit()


    caliblator = Caliblator(img)
    caliblator.chooseMode()

    
