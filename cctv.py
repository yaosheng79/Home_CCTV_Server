# Home_CCTV_Server
# CCTV 
# Created by Yigang Zhou on 2020-01-09.
# Copyright © 2020 Yigang Zhou. All rights reserved.

import cv2
import time
import threading
import datetime
from pathlib import Path
import collections

frame_queue = collections.deque(maxlen=2)
def draw_time_label(frame):
    """
    旋转frame，并加入时间label
    :param frame:
    :return:
    """
    text = time.ctime()
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.75
    color = (127, 63, 255)
    thickness = 2
    f = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)
    f = cv2.putText(f, text, (10, 30), font_face, scale, color, thickness, cv2.LINE_AA)
    frame_queue.append(f)
    return f


class CCTV():

    def __init__(self,save_path='/'):
        threading.Thread.__init__(self)
        self.cap = cv2.VideoCapture(0)
        # set resolution
        self.frame_width = 1024
        self.frame_height = 768
        self.cap.set(3, self.frame_width)
        self.cap.set(4, self.frame_height)
        self.current_hour = -1
        self.record_thread = None
        self.save_path = save_path
        print("CCTV初始化...")
        print("摄像头分辨率", self.cap.get(3), "x", self.cap.get(4), "@", self.cap.get(cv2.CAP_PROP_FPS), "fps")
        print("储存路径", self.save_path)


    def __del__(self):
        self.cap.release()

    def start_record(self):

        now = datetime.datetime.now()
        date = str(now.year)+'-'+str(now.month)+'-'+str(now.day)
        hour = now.hour


        if hour != self.current_hour:
            print(time.ctime(), hour, "!======", self.current_hour)
            path = self.save_path + date + '/'
            file_path = path + str(hour) + '.mp4'
            Path(path).mkdir(parents=True, exist_ok=True)

            if self.record_thread != None:
                self.record_thread.stop()

            self.record_thread = RecordThread(self.cap, file_path)
            self.record_thread.start()
            self.current_hour = hour
        threading.Timer(1, self.start_record).start()

    def stop_record(self):
        self.record_thread.stop()

    def get_frame(self):
        while not frame_queue:
            time.sleep(0.01)
        image = frame_queue.pop()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

class RecordThread(threading.Thread):

    def __init__(self, cap, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.cap = cap
        # rotated width and height
        self.frame_width = int(self.cap.get(4))
        self.frame_height = int(self.cap.get(3))
        print(time.ctime(), "录制停止 __init__\n")
        self.stopped = True
        out = None

    def run(self):
        print(time.ctime(), "CCTV开始录制", self.file_path)
        self.stopped = False
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        print("录制分辨率", self.cap.get(3), "x", self.cap.get(4), "@", frame_rate, "fps")

        out = cv2.VideoWriter(self.file_path, fourcc, frame_rate, (self.frame_width, self.frame_height))

        while True:
            ret, frame = self.cap.read()
            frame = draw_time_label(frame)
            if ret:
                out.write(frame)

            if self.stopped:
                # out.release()
                print(time.ctime(), "录制停止\n")
                break

    def stop(self):
        print(time.ctime(), "录制停止 stop\n")
        self.stopped = True
        self.join()
