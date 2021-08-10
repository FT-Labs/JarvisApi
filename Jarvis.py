#!/usr/bin/python

import pyttsx3
import speech_recognition as sr
import datetime
import threading
import time
import Global as g
import os
import subprocess
from pynput.keyboard import Key, Controller
import cv2
import psutil
import webbrowser




class Jarvis:

    def __init__(self):
        #Initialize pyttsx3 props
        self.engine = pyttsx3.init("espeak")
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("voices", "en-us")
        self.controller = Controller()
        self.r = sr.Recognizer()
        self.r.dynamic_energy_threshold = False
        self.cameraThread = threading.Thread(target=self.openCamera)
        self.cameraFlag = False
        self.t1 = threading.Thread(target=self.speakThread, args=("",))
    #tts
    def speak(self, audio):
        self.t1 = threading.Thread(target=self.speakThread, args=(audio,))
        self.t1.start()

    def speakThread(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()



    def runAndWait(self):
        self.engine.runAndWait()

    def greet(self):
        hour = int(time.strftime("%H"))

        if hour>=0 and hour<6:
            self.speak("Good night sir")
        elif hour>=6 and hour<=13:
            self.speak("Good morning sir")
        else:
            self.speak("Good evening sir")

    def takeCommand(self):

        while True:

            if not self.t1.is_alive():
                with sr.Microphone() as mic:
                    #print("Listening commands sir...")
                    self.r.pause_threshold = 1
                    audio = self.r.listen(mic, timeout=100, phrase_time_limit=2)

                try:
                    query = self.r.recognize_google(audio, language="en-US")
                    print(f"Admin says: {query}")

                    self.processCommand(query)

                except:
                    self.speak("I am sorry sir, can you repeat again?")
                    #return "none"

                #return query


    def openCamera(self):
        self.cameraFlag = True
        os.system("st -e mpv --no-cache --no-osc --no-input-default-bindings --profile=low-latency --input-conf=/dev/null --title=webcam $(ls /dev/video[0,2,4,6,8] | tail -n 1) &")

    def closeCamera(self):

        for proc in psutil.process_iter():
            if proc.name() == "mpv":
                proc.kill()



    def processCommand(self, command):
        lwr = str(command).lower()
        print(lwr)

        if any(x in lwr for x in g.NUMS):
            for key in g.NUMS:
                if key in lwr.split(" "):
                    if len(lwr)<=2:
                        #t1 = threading.Thread(target=self.speak, args=("Changing to desktop {}".format(key),))
                        #t1.start()
                        self.speak("Changing to desktop {}".format(key))
                        os.system("xdotool key Super_L+{}".format(key))
                        return
                    os.system("xdotool key Super_L+{}".format(key))
                    break



        if lwr.find("hi") != -1 or lwr.find("hey") != -1:
            self.greet()
        elif lwr.find("there")!=-1 and lwr.find("you")!=-1:
            self.speak("For you sir, always.")
        elif lwr.find("*") != -1:
            self.speak("Language, sir")
        elif lwr.find("open editor") != -1:
            self.speak("Opening vim, sir")
            #subprocess.call("st -e vim &")
            os.system("st -e vim &")
        elif lwr.find("terminal") != -1:
            os.system("st &")
        elif lwr.find("open cam") != -1:
            self.speak("Opening camera, sir")
            self.cameraThread.start()
        elif lwr.find("open") != -1 and lwr.find("stuff") != -1:
            self.speak("Opening your usual programs, sir.")
            os.system("st -e sudo pacman -Syu &")
            time.sleep(0.1)
            os.system("xdotool key alt+j Super_L+w")
            time.sleep(0.35)
            os.system("xdotool key Super_L+9")
            time.sleep(0.35)
            os.system("whatsapp-for-linux &")
            time.sleep(0.5)
            os.system("/home/opt/Discord/Discord &")
            time.sleep(0.5)
            os.system("telegram-desktop &")
            time.sleep(0.5)
            os.system("xdotool key Super_L+1 alt+j")
        elif self.cameraFlag and lwr.find("close cam") != -1:
            try:
                self.cameraFlag = False
                self.speak("Closing camera, sir")
                self.cameraThread._stop()
                self.closeCamera()
            except:
                pass
        elif lwr.find("youtube") != -1:
            webbrowser.open("www.youtube.com")
        elif lwr.find("shutdown") != -1:
            os.system("sudo poweroff")
        elif lwr[:6] == "google":
            self.speak(f"Searching {lwr[6:]} on google")
            webbrowser.open(g.BASE_GOOGLE_URL+lwr[7:].replace(" ", "+"))
        elif lwr.find("mute") != -1:
            os.system("pamixer -t; kill -44 $(pidof dwmblocks)")
        elif lwr.find("volume") != -1 or lwr.find("audio") != -1:
            vol = lwr.rsplit(" ", maxsplit=1)[-1]
            print("HERE")
            print(vol)
            os.system("pamixer --unmute --set-volume {}; kill -44 $(pidof dwmblocks)".format(vol))
        else:
            self.speak("Sorry sir. Unknown command.")






if __name__ == "__main__":
    jarvis = Jarvis()
    #jarvis.speak("Hi, my name is Jarvis")
    #jarvis.speak("At your service sir")
    t1 = threading.Thread(target=jarvis.takeCommand)
    t1.start()
