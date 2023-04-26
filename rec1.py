#!/usr/bin/env python

import face_recognition
import os, sys
import cv2
import numpy as np
import math
import pickle
import math
from face_recognition_admin import *
import pyvirtualcam

from PIL import Image
import numpy as np
import pickle


# Helper
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_faces = []
    name = []
    process_current_frame = True

    def __init__(self):
        self.name, self.known_faces = pickle.load(
            open("./pickled_faces/admin.pickle", "rb"))

    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f"faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]

        print(self.name)

    def run_recognition(self):
        cam = pyvirtualcam.Camera(640, 480, 30, device='/dev/video2')
        # cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('image', 600,600)
        prev_top_left = (-1, 1)
        prev_bottom_right = (1, 1)

        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        while True:
            _, frame = video_capture.read()

            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                frame = Image.fromarray(frame)
                # Get width from cv2
                face_label = FaceLabel(frame, 0, video_capture.get(3))

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for _, face_location in zip(self.face_encodings, self.face_locations):
                # results = face_recognition.compare_faces(
                #     self.known_faces, face_encoding, g.TOL)
                # match = ""
                top_left = (face_location[3]*3.5 - (face_location[1] - face_location[3])/4,
                            face_location[0]*3.5 - (face_location[2] - face_location[0])/4)
                bottom_right = (face_location[1]*4 + (face_location[1] - face_location[3])/4,
                                face_location[2]*4 + (face_location[2] - face_location[0])/4)

                # percentage_change = [top_left[0]/prev_top_left[0], top_left[1]/prev_top_left[1],
                #                      bottom_right[0]/prev_bottom_right[0], bottom_right[1]/prev_bottom_right[1]]

                # if prev_top_left[0] != -1 and not (any(1.25 < x for x in percentage_change) or any(0.75 > x for x in percentage_change)):
                #     face_label.dashed_rectangle(
                #         [prev_top_left, prev_bottom_right], name="ADMIN")
                # else:
                face_label.dashed_rectangle([top_left, bottom_right], name="ADMIN")
                # prev_top_left = top_left
                # prev_bottom_right = bottom_right


            # # Display the resulting image
            # cv2.imshow('image', np.array(frame))
            cam.send(cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2RGB))

            # # Hit 'q' on the keyboard to quit!
            # if cv2.waitKey(1) == ord('q'):
            #     break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()
