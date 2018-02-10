# -*- coding:utf-8 -*-
#!/usr/bin/python
import socket
import numpy
import cv2


def getImageSocket():
    #IPアドレスとポート番号は環境に応じて変更
#    HOST = "192.168.1.100"
    HOST = "localhost"
    PORT = 8000
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((HOST,PORT))
    sock.send(b'HELLO\n')
    buf=b""
    recvlen=100
    while recvlen>0:
        receivedbytes=sock.recv(1024*8)
        recvlen=len(receivedbytes)
        buf +=receivedbytes
    sock.close()
#    narray=numpy.fromstring(buf,dtype='uint8')
    narray=numpy.frombuffer(buf,dtype='uint8')
    return cv2.imdecode(narray,1)

if __name__ == '__main__':
#    while True:
    img = getImageSocket()
    cv2.imshow('Capture',img)
    cv2.waitKey(0)
    
#    if cv2.waitKey(100) & 0xFF == ord('q'):
#       break
