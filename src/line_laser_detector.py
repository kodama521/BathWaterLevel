import cv2
import numpy as np
import detector
import sys
import util

class LineLaserDetector(detector.Detector):
    __LASER_INTENSITY_INVALID_TH = 10
    __LASER_INTENSITY_TH = 40
    __LIGHT_ON_TH = 70

    def __init__(self):
        super().__init__()

    
    #@staticmethod
    # def __get_color_angle(tar_vect, ref_vect):  #now not used
    #     if np.linalg.norm(tar_vect) <= 5:
    #         return -1

    #     dot_xy = np.dot(tar_vect, ref_vect)
    #     norm_x = np.linalg.norm(tar_vect)
    #     norm_y = np.linalg.norm(ref_vect)
    #     cos = dot_xy / (norm_x*norm_y)
    #     return np.arccos(cos)

    @staticmethod
    def __subtract_median(img_gray):
        img_size = {"w":img_gray.shape[1], "h":img_gray.shape[0]}
        ret_img = img_gray.copy()
#        median_b_val = np.median(ret_img[:,:,0])
#        median_g_val = np.median(ret_img[:,:,1])
#        median_r_val = np.median(ret_img[:,:,2])
        median_val = np.median(ret_img[:,:])

        for y in range(img_size['h']):
            for x in range(img_size['w']):
                # ret_img[y,x,0] = 0 if ret_img[y,x,0] < median_b_val else ret_img[y,x,0] - median_b_val
                # ret_img[y,x,1] = 0 if ret_img[y,x,1] < median_g_val else ret_img[y,x,1] - median_g_val
                # ret_img[y,x,2] = 0 if ret_img[y,x,2] < median_r_val else ret_img[y,x,2] - median_r_val
                ret_img[y,x] = 0 if ret_img[y,x] < median_val else ret_img[y,x] - median_val

        return ret_img

    @classmethod
    def __get_laser_gray_img(cls, img, red_th):
        img_size = {"w":img.shape[1], "h":img.shape[0]}
        red_img = img.copy()[:,:,2]
        sub_red_img = cls.__subtract_median(red_img.copy())

#        angle_img = sub_img.copy()[:,:,2]

        for y in range(img_size['h']):
            for x in range(img_size['w']):
                # tmp_angle = cls.__get_color_angle(sub_img[y,x], [0,0,1])
                # print(tmp_angle)

                # if (tmp_angle > np.pi / 8) or (tmp_angle == -1):
                #     red_img[y,x] = 0
                #     #debug
                #     angle_img[y,x] = 0
                # else:
                #     angle_img[y,x] = (int)(tmp_angle * 100)

                if (sub_red_img[y,x] < red_th):
                    sub_red_img[y,x] = 0

        #debug
#         cv2.imshow("img", img)
#         cv2.imshow("sub_red_img", sub_red_img)
#         cv2.imshow("red_img", red_img)

# # #        cv2.imshow("angle_img", angle_img)
        
#         cv2.waitKey(0)
        
        return sub_red_img

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

    @staticmethod
    def __img2arr(gray_img):
        ret_arr = []
        for y in range(gray_img.shape[0]):
            for x in range(gray_img.shape[1]):
                ret_arr.append(gray_img[y,x])

        return np.array(ret_arr)

    @staticmethod
    def __get_sperior_arr(arr, num):
#        print(num, len(arr))
#        print(np.argpartition(arr, -num)[-num:])

        return np.array(arr)[np.argpartition(arr, -num)[-num:]]

    def __get_laser_intensity(self, gray_area_img):
#        pix_val_sum = 0.0
#        mask_count = 0

        img_arr = self.__img2arr(gray_area_img.copy())
        img_arr_nonzero = img_arr[img_arr.nonzero()]

        if len(img_arr_nonzero) == 0:
            return 0

        img_arr_sperior = self.__get_sperior_arr(img_arr_nonzero, int(len(img_arr_nonzero)*0.1))

        ret_val = np.average(img_arr_sperior)
#        print('intensity = ', ret_val)
        return ret_val

        # for y in range(gray_area_img.shape[0]):
        #     for x in range(gray_area_img.shape[1]):
        #         if gray_area_img[y,x] > 0:
        #             pix_val_sum += gray_area_img[y, x]
        #             mask_count += 1

        # if mask_count == 0:
        #     return 0
        # else:
        #     ret_val = pix_val_sum / mask_count
        #     print('line_intensity=', ret_val)
        #     return ret_val

    @classmethod
    def __detect_light_on(cls, gray_img):
        pix_val_sum = 0.0
        for y in range(gray_img.shape[0]):
            for x in range(gray_img.shape[1]):
                pix_val_sum += gray_img[y,x]

        val = (pix_val_sum / (gray_img.shape[0] * gray_img.shape[1]))
#        print(val)
        return val > cls.__LIGHT_ON_TH

    def detect(self, mode='laser'):
        if not self._inited:
            print('input image!!')
            return LineLaserDetector.RESULT_ERROR

        tmp_gray_rotate_img = cv2.cvtColor(self._img_resize, cv2.COLOR_RGB2GRAY)
#        cv2.imshow("debug_gray_img", tmp_gray_rotate_img)
        if LineLaserDetector.__detect_light_on(tmp_gray_rotate_img):
            return LineLaserDetector.RESULT_INVALID_ENV
        else:
            if mode == 'on_off':
                return LineLaserDetector.RESULT_VALID_ENV

            elif mode == 'laser':
                clip_img = self.__get_clip_area_img(self._img_rotate)
#                tmp_gray_clip_img = self.__get_laser_gray_img(clip_img, 0)
#                th, _ = cv2.threshold(tmp_gray_clip_img, 0, 1, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                        
                gray_img = self.__get_laser_gray_img(clip_img, 10)
                #gray_img = self.__get_laser_gray_img(self._img_rotate, 10)
#                print('th =',th)
            
                line_intensity = self.__get_laser_intensity(gray_img)

                if line_intensity < LineLaserDetector.__LASER_INTENSITY_INVALID_TH:
                    return LineLaserDetector.RESULT_ERROR
                
                if line_intensity < LineLaserDetector.__LASER_INTENSITY_TH and\
                   line_intensity > LineLaserDetector.__LASER_INTENSITY_INVALID_TH:
                    return LineLaserDetector.RESULT_FULL

                return LineLaserDetector.RESULT_NOT_FULL

            else:
                return LineLaserDetector.RESULT_ERROR

if __name__ == '__main__':
    # IMG_NAME1 = '../test_img/IMG_7645.JPG'
    # IMG_NAME2 = '../test_img/IMG_7644.JPG'
    # IMG_NAME3 = '../test_img/test.JPG'
    IMG_NAME1 = '../test_img/result_not_full12.png'
    IMG_NAME2 = '../test_img/result_full13.png'
    IMG_NAME3 = '../test_img/result_full1_err.png'
    IMG_SIZE =(320 ,240)
    MIN_LINE_LEMGTH = 20
    MAX_LINE_GAP = 50

    img1 = cv2.imread(IMG_NAME1)
    img2 = cv2.imread(IMG_NAME2)
    img3 = cv2.imread(IMG_NAME3)
    if img1 is None or img2 is None:
        print ('no image!!')
        sys.exit()

    img1 = cv2.resize(img1, IMG_SIZE)
    img2 = cv2.resize(img2, IMG_SIZE)
    img3 = cv2.resize(img3, IMG_SIZE)

    line_laser_detector = LineLaserDetector()
    line_laser_detector.input_img(img1)
    result1 = line_laser_detector.detect()

    line_laser_detector.input_img(img2)
    result2 = line_laser_detector.detect()

    line_laser_detector.input_img(img3)
    result3 = line_laser_detector.detect()
    
    print('result1 =', result1)
    print('result2 =', result2)
    print('result3 =', result3)

    cv2.imshow("img1", img1)
    cv2.imshow("img2", img2)
    cv2.imshow("img3", img3)

    cv2.waitKey(0)
