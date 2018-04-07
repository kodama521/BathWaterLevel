# -*- coding:utf-8 -*-
#!/usr/bin/python

import sys
import socketserver
import cv2

class TCPHandler(socketserver.BaseRequestHandler):
    #リクエストを受け取るたびに呼ばれる関数
    def handle(self):
#        while True:
        #HELLOを受け取ったらJPEG圧縮したカメラ画像を文字列にして送信
        rcv_data = self.request.recv(1024).strip()
        if rcv_data == b'HELLO':
            _, frame = capture.read()
            jpegstring = cv2.imencode('.jpeg',frame)[1].tostring()
            self.request.send(jpegstring)
        

#環境に応じて変更
#HOST = '192.168.1.101'
HOST = 'localhost'
PORT = 8000

#カメラの設定
capture = cv2.VideoCapture(0)
capture.set(3,320)
capture.set(4,240)
if not capture:
    print("Could not open camera")
    sys.exit()

socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer((HOST, PORT), TCPHandler)
server.capture = capture
#^Cを押したときにソケットを閉じる
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
server.shutdown()
sys.exit()
