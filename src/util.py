# -*- coding: utf-8 -*-

import csv

def readConfig():
    calib_data = {"angle":[0],
                  "level":[0],
                  "area":[0, 0, 0, 0]}

    try:
        with open('../config.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                for col in range(len(row[1:])):
                    calib_data[row[0]] = [int(col) for col in row[1:]]

    except FileNotFoundError:
        print('config.csv not found. return default falue!')
        calib_data

    print('calib_data =', calib_data)

    return calib_data

def transPosCenterBase(x=None, y=None, center_x=None, center_y=None):
    ret_x = None
    ret_y = None

    if x is not None:
        ret_x = x - center_x

    if y is not None:
        ret_y = center_y - y

    return ret_x, ret_y

def transPosOriginal(x=None, y=None, center_x=None, center_y=None):
    ret_x = ret_y = None

    if x is not None:
        ret_x = x + center_x

    if y is not None:
        ret_y = center_y - y

    return ret_x, ret_y

if __name__ == '__main__':
    readConfig()
