#!/usr/bin/python

import pyttsx3
import speech_recognition as sr
import threading
import time
import globs as g
import os
from pynput.keyboard import Controller
import psutil
import webbrowser
from face_recognition import FaceRecognition
import pyaudio
import websockets
import asyncio
import base64
import json


FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class Jarvis:

    def __init__(self):
        #Initialize pyttsx3 props
        self.engine = pyttsx3.init("espeak")
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("voices", "en-us")
        self.controller = Controller()
        self.r = sr.Recognizer()
        self.r.dynamic_energy_threshold = False
        self.camera_thread = threading.Thread(target=self.openCamera)
        self.camera_flag = False
        self.thread_speak = threading.Thread(target=self.speakThread, args=("",), daemon=True)
        self.face_recognition = FaceRecognition()
        self.thread_face_recognition = threading.Thread(target=self.face_recognition.open_video)
        self.thread_speech_recognition = threading.Thread(target=self.start_asyncio, daemon=True)

        self.res = "-1"



    def start_asyncio(self):
        asyncio.run(self.send_receive_data())


    def change_number_string(self, command):
        command = command.replace("one", "3")
        command = command.replace("two", "2")
        command = command.replace("three", "3")
        command = command.replace("four", "4")
        command = command.replace("five", "5")
        command = command.replace("six", "6")
        command = command.replace("seven", "7")
        command = command.replace("eight", "8")
        command = command.replace("nine", "9")
        return command


    async def send_receive_data(self):
        async with websockets.connect(
            g.SOCKET_ENDPOINT,
            extra_headers=(("Authorization", g.API_KEY),),
            ping_interval=5,
            ping_timeout=20
                ) as _ws:
            await asyncio.sleep(0.1)
            print("Receiving session begins...")
            session_begins = await _ws.recv()
            print(session_begins)
            async def send():
                while True:
                    try:
                        data = stream.read(FRAMES_PER_BUFFER)
                        data = base64.b64encode(data).decode("utf-8")
                        json_data = json.dumps({"audio_data" : str(data)})
                        await _ws.send(json_data)
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break
                    except Exception as e:
                        assert False, "Not a websocket 4008 error"
                    await asyncio.sleep(0.01)

                return True

            async def receive():
                flag = False
                old = ""
                counter = 0
                while True:
                    try:
                        result_str = await _ws.recv()
                        res = str(json.loads(result_str)["text"]).lower()
                        res = res.strip(".")

                        if res != "" and old in res:
                            old = res
                            print(old)
                        else:
                            self.res = old

                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break
                    except Exception as e:
                        assert False, "Not a 4008 websocket error"

            send_result, receive_result = await asyncio.gather(send(), receive())


    #tts
    def speak(self, audio):
        self.thread_speak = threading.Thread(target=self.speakThread, args=(audio,))
        self.thread_speak.start()

    def speakThread(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def resetThreads(self):
        self.thread_face_recognition = threading.Thread(target=self.face_recognition.open_video)
        self.thread_face_recognition.start()

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
        self.thread_speech_recognition.start()
        res = self.res

        while True:

            if res not in self.res:
                self.processCommand(self.res)
                res = self.res
                time.sleep(1.5)



    def openCamera(self):
        self.cameraFlag = True
        os.system("st -e mpv --no-cache --no-osc --no-input-default-bindings --profile=low-latency --input-conf=/dev/null --title=webcam $(ls /dev/video[0,2,4,6,8] | tail -n 1) &")

    def closeCamera(self):

        for proc in psutil.process_iter():
            if proc.name() == "mpv":
                proc.kill()



    def processCommand(self, command):
        lwr = str(command).lower()
        print(command)

        if any(x in lwr for x in g.NUMS):
            for key in g.NUMS:
                if key in lwr.split(" "):
                    if len(lwr)<=2:
                        self.speak("Changing to desktop {}".format(key))
                        os.system("xdotool key Super_L+{}".format(key))
                        return
                    os.system("xdotool key Super_L+{}".format(key))
                    break



        if len(lwr) < 8 and lwr.find("hi") != -1 or lwr.find("hey") != -1:
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
            os.system("st -e sudo pacman -Syu &; disown")
            time.sleep(0.1)
            os.system("xdotool key alt+j Super_L+w")
            time.sleep(2)
            os.system("xdotool key Super_L+9")
            time.sleep(0.35)
            os.system("whatsapp-for-linux & ; disown")
            time.sleep(3)
            os.system("/home/opt/Discord/Discord & ; disown")
            time.sleep(3)
            os.system("telegram-desktop & ; disown")
            time.sleep(3)
            os.system("xdotool key Super_L+1 alt+j")
        elif self.cameraFlag and lwr.find("close cam") != -1:
            try:
                self.cameraFlag = False
                self.speak("Closing camera, sir")
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
            os.system("pamixer --unmute --set-volume {}; kill -44 $(pidof dwmblocks)".format(vol))
        elif lwr.find("eye") != -1 and lwr.find("open") != -1:
            self.resetThreads()
            self.speak("Opening camera, sir")

        if self.thread_face_recognition.is_alive():
            if lwr.find("see me") != -1:
                self.speak("Yes")
                self.face_recognition.is_label = True
            elif self.face_recognition.is_label and lwr.find("am i") != -1:
                self.speak("admin")
                self.face_recognition.is_name = True
            elif lwr.find("close") != -1 or lwr.find("lowe") != -1:
                self.face_recognition.close_video()
                self.resetThreads()




if __name__ == "__main__":
    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
            )


    jarvis = Jarvis()
    jarvis.takeCommand()
#    t1 = threading.Thread(target=jarvis.takeCommand)
#    t1.start()
