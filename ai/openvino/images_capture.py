import cv2

class ImagesCapture:
    def __init__(self, input_source, loop=False):
        self.loop = loop
        if isinstance(input_source, str) and input_source.isdigit():
            input_source = int(input_source)
        self.cap = cv2.VideoCapture(input_source)
        if not self.cap.isOpened():
            raise RuntimeError("Can't open input source")
        
    def read(self):
        has_frame, frame = self.cap.read()
        if has_frame:
            return frame
        if self.loop:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            has_frame, frame = self.cap.read()
            if has_frame:
                return frame
        return None

    def get_type(self):
        return 'VIDEO'

    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

def open_images_capture(input_source, loop=False):
    return ImagesCapture(input_source, loop) 