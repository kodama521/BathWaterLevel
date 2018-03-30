import cv2
import numpy as np
import detector
import sys
import util

class LineLaserDetector(detector.Detector):
    __LASER_INTENSITY_TH = 100

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

    def __get_clip_area_img(self, img):
        start_x, start_y = util.transPosOriginal(x=self._calib_data["area"][0],
                                                 y=self._calib_data["area"][3],
                                                 center_x=self._center["x"],
                                                 center_y=self._center["y"])

        end_x, end_y = util.transPosOriginal(x=self._calib_data["area"][2],
                                             y=self._calib_data["area"][1],
                                             center_x=self._center["x"],
                                             center_y=self._center["y"])

        return img[start_y:end_y, start_x:end_x, :]

    def __get_laser_intensity(self, gray_area_img):
        pix_val_sum = 0.0
        mask_count = 0
        for y in range(gray_area_img.shape[0]):
            for x in range(gray_area_img.shape[1]):
                if gray_area_img[y,x] > 0:
                    pix_val_sum += gray_area_img[y, x]
                    mask_count += 1

        return pix_val_sum / mask_count

    def detect(self):
        if not self._inited:
            print('input image!!')

        clip_img = self.__get_clip_area_img(self._img_rotate)
        tmp_gray_img = self.__get_raser_gray_img(clip_img, 0)
        th, _ = cv2.threshold(tmp_gray_img, 0, 1, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        gray_img = self.__get_raser_gray_img(self._img_rotate, th)

        line_intensity = self.__get_laser_intensity(gray_img)
        

        return (line_intensity > LineLaserDetector.__LASER_INTENSITY_TH)



    

if __name__ == '__main__':
    IMG_NAME1 = '../test_img/IMG_7645.JPG'
    IMG_NAME2 = '../test_img/IMG_7644.JPG'
    IMG_SIZE =(320 ,240)
    MIN_LINE_LEMGTH = 20
    MAX_LINE_GAP = 50

    img1 = cv2.imread(IMG_NAME1)
    img2 = cv2.imread(IMG_NAME2)
    if img1 is None or img2 is None:
        print ('no image!!:', IMG_NAME)
        sys.exit()

    img1 = cv2.resize(img1, IMG_SIZE)
    img2 = cv2.resize(img2, IMG_SIZE)

    line_laser_detector = LineLaserDetector()
    line_laser_detector.input_img(img1)
    result1 = line_laser_detector.detect()

    line_laser_detector.input_img(img2)
    result2 = line_laser_detector.detect()

    print('line_intensity1 =', result1)
    print('line_intensity2 =', result2)
    
