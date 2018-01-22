# -*- coding: utf-8 -*-

import csv

def readConfig():
    calib_data = {}
    with open('config.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            calib_data[row[0]] = int(row[1])
            
        print('calib_data =', calib_data)

        return calib_data

if __name__ == '__main__':
    readConfig()
