import cv2
import numpy as np
import detector
import sys
import util

class LineLaserDetector(detector.Detector):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __get_raser_gray_img(img, red_th):
        img_size = {"w":img.shape[1], "h":img.shape[0]}
        red_img = img.copy()[:,:,2]

        for y in range(img_size['h']):
            for x in range(img_size['w']):
                if (red_img[y,x] < red_th):
                    red_img[y,x] = 0

        return red_img

    @staticmethod
    def __get_lines(img, min_line_length, max_line_gap):
        img_size = {"w":img.shape[1], "h":img.shape[0]}
        lines = cv2.HoughLines(img,1,np.pi/180,100)

        ret_img = np.zeros((img_size['h'], img_size['w'], 3), np.uint8)

        for line in lines[:2]:
            for rho,theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))

                cv2.line(ret_img,(x1,y1),(x2,y2),(0,0,255),2)

        return ret_img

    def detect(self):
#        gray_img = self.__get_raser_gray_img(img, 50)
#        edge_img = cv2.Canny(gray_img, 50, 50, apertureSize = 3)
#        line_img = self.__get_lines(edge_img, MIN_LINE_LEMGTH, MAX_LINE_GAP)

        if not self._inited:
            print('input image!!')

        
        return self._img_rotate

#        return gray_img, edge_img, line_img


    

if __name__ == '__main__':
    IMG_NAME = '../test_img/IMG_7645.JPG'
    IMG_SIZE =(320 ,240)
    MIN_LINE_LEMGTH = 20
    MAX_LINE_GAP = 50


    img = cv2.imread(IMG_NAME)
    if img is None:
        print ('no image!!:', IMG_NAME)
        sys.exit()

    img = cv2.resize(img, IMG_SIZE)

    line_laser_detector = LineLaserDetector()
    gray_img, edge_img, line_img = line_laser_detector.detect(img)

    line_laser_detector.input_img(img)
    cv2.imshow('input_img', img)
    cv2.imshow('edge_img', edge_img)
    cv2.imshow('line_img', line_img)
    cv2.waitKey(0)

