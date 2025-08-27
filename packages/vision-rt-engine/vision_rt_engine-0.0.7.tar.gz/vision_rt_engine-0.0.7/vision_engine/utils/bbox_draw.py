#!/usr/bin/env python

import numpy as np
import cv2 as cv


class RectangleDrawer:
    def __init__(self):
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.image = None

    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.drawing = True
        elif event == cv.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)
        elif event == cv.EVENT_LBUTTONUP:
            self.end_point = (x, y)
            self.drawing = False
            cv.rectangle(self.image, self.start_point, self.end_point, (0, 255, 0), 2)

    def run(self, image: np.ndarray):
        wname = 'Mark Region'
        cv.namedWindow(wname)
        cv.setMouseCallback(wname, self.draw_rectangle)

        self.image = image
        while True:
            display_image = image.copy()
            if self.start_point and self.end_point and self.drawing:
                cv.rectangle(display_image, self.start_point, self.end_point, (0, 255, 0), 2)

            cv.imshow(wname, display_image)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()
        return np.array([*self.start_point, *self.end_point], dtype=np.float32)
