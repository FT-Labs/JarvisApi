#!/usr/bin/python
import cv2
import os
import face_recognition
import matplotlib.pyplot as plt
from FaceLabel import FaceLabel
from PIL import Image
import numpy as np
import pickle
import Global as g
import sys


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
