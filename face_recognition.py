#!/usr/bin/python
import cv2
import face_recognition
from PIL import ImageDraw, ImageFont
import math

from PIL import Image
import numpy as np
import pickle
import globs as g

class FaceRecognition:

    def __init__(self):
        self.name, self.known_faces = pickle.load(
            open("./pickled_faces/admin.pickle", "rb"))
        self.is_label = False
        self.is_name = False
        self.close_cam = False

    def close_video(self):
        self.is_label = False
        self.is_name = False
        self.close_cam = True

    def open_video(self):

        vid = cv2.VideoCapture(-1)

        while vid.isOpened():
            ret, image = vid.read()

            if self.is_label:
                prev_top_left = (-1, 1)
                prev_bottom_right = (1, 1)

                locations = face_recognition.face_locations(
                    image, number_of_times_to_upsample=0, model=g.MODEL)
                encodings = face_recognition.face_encodings(image, locations)

                image = Image.fromarray(image)
                # Get width from cv2
                face_label = FaceLabel(image, 0, vid.get(3))

                for face_encoding, face_location in zip(encodings, locations):
                    results = face_recognition.compare_faces(
                        self.known_faces, face_encoding, g.TOL)
                    match = ""
                    if any(results):

                        if self.is_name:
                            match = self.name

                        top_left = (face_location[3] - (face_location[1] - face_location[3])/4,
                                    face_location[0] - (face_location[2] - face_location[0])/4)
                        bottom_right = (face_location[1] + (face_location[1] - face_location[3])/4,
                                        face_location[2] + (face_location[2] - face_location[0])/4)

                        percentage_change = [top_left[0]/prev_top_left[0], top_left[1]/prev_top_left[1],
                                             bottom_right[0]/prev_bottom_right[0], bottom_right[1]/prev_bottom_right[1]]

                        if prev_top_left[0] != -1 and not (any(1.25 < x for x in percentage_change) or any(0.75 > x for x in percentage_change)):
                            face_label.dashed_rectangle(
                                [prev_top_left, prev_bottom_right], name=match)
                        else:
                            face_label.dashed_rectangle(
                                [top_left, bottom_right], name=match)
                            prev_top_left = top_left
                            prev_bottom_right = bottom_right

            cv2.imshow("Jarvis Cam", np.array(image))

            if self.close_cam:
                vid.release()
                cv2.destroyAllWindows()
                self.close_cam = False
                return


            if cv2.waitKey(1) & 0xFF == ord('q'):
                vid.release()
                cv2.destroyAllWindows()
                return

FONT_PATH = "./fonts/terminus-ttf-4.49.1/TerminusTTF-Bold-4.49.1.ttf"


class FaceLabel(ImageDraw.ImageDraw):

    def __init__(self, image, min_x, max_x):
        super().__init__(image)
        self.min_x = min_x
        self.max_x = max_x
        self.font = ImageFont.truetype(FONT_PATH, 24)

    def draw_text(self, xy, name):
        self.text(xy, name.upper(), font=self.font, fill="white")


    def thick_line(self, xy, direction, fill=None, width=0):
        #xy – Sequence of 2-tuples like [(x, y), (x, y), ...]
        #direction – Sequence of 2-tuples like [(x, y), (x, y), ...]
        if xy[0] != xy[1]:
            self.line(xy, fill = fill, width = width)
        else:
            x1, y1 = xy[0]
            dx1, dy1 = direction[0]
            dx2, dy2 = direction[1]
            if dy2 - dy1 < 0:
                x1 -= 1
            if dx2 - dx1 < 0:
                y1 -= 1
            if dy2 - dy1 != 0:
                if dx2 - dx1 != 0:
                    k = - (dx2 - dx1)/(dy2 - dy1)
                    a = 1/math.sqrt(1 + k**2)
                    b = (width*a - 1) /2
                else:
                    k = 0
                    b = (width - 1)/2
                x3 = x1 - math.floor(b)
                y3 = y1 - int(k*b)
                x4 = x1 + math.ceil(b)
                y4 = y1 + int(k*b)
            else:
                x3 = x1
                y3 = y1 - math.floor((width - 1)/2)
                x4 = x1
                y4 = y1 + math.ceil((width - 1)/2)
            self.line([(x3, y3), (x4, y4)], fill = fill, width = 1)
        return



    def round_rectangle(self, xy, size, pos, fill="cyan"):
        self.rounded_rectangle(xy, radius=size/3, fill=fill)

        if pos == "top_left":
            self.rectangle([(xy[0][0] + size/2, xy[0][1]), (xy[1][0] + size, xy[1][1])], fill=fill)
            self.rectangle([(xy[0][0] , xy[0][1] + size / 2), (xy[1][0], xy[1][1] + size)], fill=fill)
        elif pos == "top_right":
            self.rectangle([(xy[0][0] -  size, xy[0][1]), (xy[1][0] - size/2, xy[1][1])], fill=fill)
            self.rectangle([(xy[0][0] , xy[0][1] + size/2), (xy[1][0] , xy[1][1] + size)], fill=fill)
        elif pos == "bottom_left":
            self.rectangle([(xy[0][0] +  size/2, xy[0][1]), (xy[1][0] + size, xy[1][1])], fill=fill)
            self.rectangle([(xy[0][0] , xy[0][1] - size), (xy[1][0] , xy[1][1] - size/2)], fill=fill)
        elif pos == "bottom_right":
            self.rectangle([(xy[0][0] -  size, xy[0][1]), (xy[1][0] - size/2, xy[1][1])], fill=fill)
            self.rectangle([(xy[0][0] , xy[0][1] - size), (xy[1][0] , xy[1][1] - size/2)], fill=fill)



    def dashed_line(self, xy, dash=(2,2), fill=None, width=0):
        #xy – Sequence of 2-tuples like [(x, y), (x, y), ...]
        for i in range(len(xy) - 1):
            x1, y1 = xy[i]
            x2, y2 = xy[i + 1]
            x_length = x2 - x1
            y_length = y2 - y1
            length = math.sqrt(x_length**2 + y_length**2)
            dash_enabled = True
            postion = 0
            while postion <= length:
                for dash_step in dash:
                    if postion > length:
                        break
                    if dash_enabled:
                        start = postion/length
                        end = min((postion + dash_step - 1) / length, 1)
                        self.thick_line([(round(x1 + start*x_length),
                                          round(y1 + start*y_length)),
                                         (round(x1 + end*x_length),
                                          round(y1 + end*y_length))],
                                        xy, fill, width)
                    dash_enabled = not dash_enabled
                    postion += dash_step
        return


    def dashed_rectangle(self, xy, dash=(2, 2), outline="cyan", width=0, name=""):
        #xy - Sequence of [(x1, y1), (x2, y2)] where (x1, y1) is top left corner and (x2, y2) is bottom right corner
        x1, y1 = xy[0]
        x2, y2 = xy[1]
        min_size = min(x2-x1, y2-1)
        rect_factor = min_size/25
        width = round(rect_factor/3)
        dash = (min_size / 9, min_size / 18)
        halfwidth1 = math.floor((width - 1)/2)
        halfwidth2 = math.ceil((width - 1)/2)
        min_dash_gap = min(dash[1::2])
        end_change1 = halfwidth1 + min_dash_gap + 1
        end_change2 = halfwidth2 + min_dash_gap + 1
        odd_width_change = (width - 1)%2
        self.round_rectangle([(x1 - rect_factor/2, y1 - rect_factor/2), (x1 + rect_factor/2, y1 + rect_factor/2)], rect_factor, "top_left")
        self.dashed_line([(x1 - halfwidth1, y1), (x2 - end_change1, y1)],
                         dash, outline, width)
        self.rectangle([((x1 + x2)/2 - halfwidth1 , y1), ((x1 + x2)/2 + halfwidth1, y1 + dash[0]*2/3)], fill="cyan")
        self.round_rectangle([(x2 - rect_factor/2, y1 - rect_factor/2), (x2 + rect_factor/2, y1 + rect_factor/2)], rect_factor, "top_right")
        self.dashed_line([(x2, y1 - halfwidth1), (x2, y2 - end_change1)],
                         dash, outline, width)
        if name != "":
            self.draw_text((x2 + 8, abs(y2 + y1)/2 - 48), name)
        self.rectangle([(x2 - dash[0]*2/3, (y1+y2)/2 - halfwidth1), (x2, (y1+y2)/2 +halfwidth1)], fill="cyan")
        self.round_rectangle([(x2 - rect_factor/2, y2 - rect_factor/2), (x2 + rect_factor/2, y2 + rect_factor/2)], rect_factor, "bottom_right")
        self.dashed_line([(x2 + halfwidth2, y2 + odd_width_change),
                          (x1 + end_change2, y2 + odd_width_change)],
                         dash, outline, width)
        self.rectangle([((x1 + x2)/2 - halfwidth1 , y2), ((x1 + x2)/2 + halfwidth1, y2 - dash[0]*2/3)], fill="cyan")
        self.round_rectangle([(x1 - rect_factor/2, y2 - rect_factor/2), (x1 + rect_factor/2, y2 + rect_factor/2)], rect_factor, "bottom_left")
        self.dashed_line([(x1 + odd_width_change, y2 + halfwidth2),
                          (x1 + odd_width_change, y1 + end_change2)],
                         dash, outline, width)
        self.rectangle([(x1, (y1+y2)/2 - halfwidth1), (x1 + dash[0]*2/3, (y1+y2)/2 +halfwidth1)], fill="cyan")
        return
