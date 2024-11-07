# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        context = ''
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self, file_path):
        # file_object = open(file_path, 'rb')
        # try:
        #     index = 1
        #     while True:
        #         chunk = file_object.read(1280)
        #         if not chunk:
        #             break
        #         self.ws.send(chunk)

        #         index += 1
        #         time.sleep(0.04)
        # finally:
        #     file_object.close()

        # self.ws.send(bytes(self.end_tag.encode('utf-8')))
        # 参数设置
        FORMAT = pyaudio.paInt16  # 16位深度
        CHANNELS = 1              # 单声道
        RATE = 16000              # 采样率 16kHz
        CHUNK = 1280              # 每个缓冲区的帧数    
        p = pyaudio.PyAudio()
        stream = p.open(rate=RATE, 
                        format=FORMAT,
                        channels=CHANNELS,
                        frames_per_buffer=CHUNK,
                        input=True)
        while True:
            data = stream.read(CHUNK)
            self.ws.send(data)


    def  recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    words = []
                    json_data = result_1['data']
                    data = json.loads(json_data)
                    text = ''
                    for item in data['cn']['st']['rt']:
                        for ws in item['ws']:
                            for cw in ws['cw']:
                                # words.append(cw['w'])
                                text += cw['w']
                # print("rtasr result: " + result_1["data"])
                    context +=text
                    print(context)
                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


if __name__ == '__main__':
    logging.basicConfig()

    app_id = "ade84ce6"
    api_key = "aeca749835e4dfa84cd2bf2192c1135b"
    file_path = r"./python/test_1.pcm"

    client = Client()
    client.send(file_path)