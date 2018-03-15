# -*- coding:utf-8 -*-
#!/usr/bin/python
import socket
import numpy
import cv2


class ClientImg(object):
    #    HOST = "192.168.1.100"
    #    PORT = 8000

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self):
        self.__socket.connect((self.__host, self.__port))

    def getImageSocket(self):
        #IPアドレスとポート番号は環境に応じて変更
        sended_bytes = self.__socket.send(b'HELLO\n')
        print('message send:', sended_bytes)
        
        buf=b""
        recvlen=100
        while recvlen > 0:
            receivedbytes=self.__socket.recv(1024*8)
            recvlen=len(receivedbytes)
            buf +=receivedbytes
        #    narray=numpy.fr/omstring(buf,dtype='uint8')

        narray=numpy.frombuffer(buf,dtype='uint8')
        print('bufsize =', len(buf))
        return cv2.imdecode(narray,1)

if __name__ == '__main__':
#    HOST = "192.168.1.100"
    HOST = "localhost"
    PORT = 8000

    while True:
        client_img = ClientImg(HOST, PORT)
        client_img.connect()
        img = client_img.getImageSocket()
        cv2.imshow('Capture',img)
        cv2.waitKey(0)
