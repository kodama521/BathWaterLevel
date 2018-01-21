# -*- coding: utf-8 -*-

import cv2
import sys
import math
import sys #for debug (main)
import numpy as np

class Cv2ImgRotator(object):
    def __init__(self, img, callback=None):
        #入力画像
        self.__img = self.__resize(img)
        self.__img_rot = self.__img.copy()

        self.__img_size_tupple = (self.__img.shape[1], self.__img.shape[0])
        self.__center = {"x":self.__img.shape[1]/2, "y":self.__img.shape[0]/2}
        self.__center_tupple = (self.__center["x"], self.__center["y"])

        self.__pt1 = {"x":0, "y":0}
        self.__pt2 = {"x":0, "y":0}
        self.__rotating = False
        self.__angle_rad = 0
        self.__angle_rad_sum = 0
        self.__callback = callback


    @staticmethod
    def __resize(img):
        diag_size = int(math.hypot(img.shape[1], img.shape[0]))
        size = (diag_size, diag_size, 3)
        overlay_img = np.zeros(size, dtype=np.uint8)
        center = {"x":int(overlay_img.shape[1]/2), "y":int(overlay_img.shape[0]/2)}
        st_overlay = {"x":center["x"] - int(img.shape[1]/2),
                      "y":center["y"] - int(img.shape[0]/2)}
        ed_overlay = {"x":st_overlay["x"] + img.shape[1],
                      "y":st_overlay["y"] + img.shape[0]}

        overlay_img[st_overlay["y"]:ed_overlay["y"],
                    st_overlay["x"]:ed_overlay["x"]] = img

        return overlay_img.copy()

    def __mouseCallback(self, eventType, x, y, flags, userdata):
        if eventType == cv2.EVENT_LBUTTONDOWN:
            self.__pt1["x"] = x - self.__center["x"]
            self.__pt1["y"] = self.__center["y"] - y
            self.__rotating = True

        elif eventType == cv2.EVENT_MOUSEMOVE and self.__rotating:
            self.__pt2["x"] = x - self.__center["x"]
            self.__pt2["y"] = self.__center["y"] - y

            self.__angle_rad = (math.atan2(self.__pt2["y"], self.__pt2["x"])
                             - math.atan2(self.__pt1["y"], self.__pt1["x"]))

            rotate_deg = math.degrees(self.__angle_rad)

            rotate_matrix = cv2.getRotationMatrix2D(self.__center_tupple, rotate_deg, 1.0)
            self.__img_rot = cv2.warpAffine(self.__img,
                                            rotate_matrix,
                                            self.__img_size_tupple,
                                            flags=cv2.INTER_CUBIC)

        elif eventType == cv2.EVENT_LBUTTONUP:
            self.__rotating = False
            self.__img = self.__img_rot.copy()
            self.__angle_rad_sum += self.__angle_rad

    def getResizeImg(self):
        return self.__img

    def rotate(self):
        window_name = "rotate!"
        cv2.imshow(window_name, self.__img_rot)
        cv2.setMouseCallback(window_name, self.__mouseCallback, None)

        while True:
            cv2.imshow(window_name, self.__img_rot)
            if cv2.waitKey(30) == 27:
                cv2.destroyWindow("rotate!")
                break
            

        return int(math.degrees(self.__angle_rad_sum)), self.__img


#for debug
if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 1:
        print ('please input image name')
        sys.exit()

    img = cv2.imread(args[1])
    if img is None:
        print ('no image!!:', img_name)
        sys.exit()

    img_rotator = Cv2ImgRotator(img)

    angle, rotate_img = img_rotator.rotate()

    print ("angle = ", angle)
    
    cv2.imshow('rotate_img', rotate_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

