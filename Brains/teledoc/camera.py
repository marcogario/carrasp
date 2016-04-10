import time
import base64

import cv2


class Camera(object):
    def __init__(self, namespace):
        self.ns = namespace
        self.cam = None

    def setup(self):
        self.cam = cv2.VideoCapture(0)

    def control_loop(self):
        print("Teledoc: Camera control_loop has started")
        while not self.ns.do_quit:
            self.update_frame()
            time.sleep(self.ns.camera_freq) # 1.0 / 30.0
        self.cam.release()
        print("Teledoc: Camera control_loop has stopped")

    def update_frame(self):
        if self.cam.isOpened():
            success, image = self.cam.read()
            if success:
                # We are using Motion JPEG, but OpenCV defaults to capture raw images,
                # so we must encode it into JPEG in order to correctly display the
                # video stream.
                small = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
                ret, jpeg = cv2.imencode('.jpg', small)
                if ret:
                    self.ns.frame = jpeg.tostring()
                    print("Teledoc Camera: Updated Frame")

    def get_frame_base64(self):
        f = self.ns.frame
        return base64.b64encode(f)

if __name__ == "__main__":
    class MockNamespace(object):
        frame = None
        camera_freq = (1.0 / 3.0)

    ns = MockNamespace()
    print("Testing Camera connection...")
    c = Camera(ns)
    c.cam = cv2.VideoCapture(0)
    time.sleep(1)
    c.update_frame()
    print(c.get_frame_base64())
    c.cam.release()
