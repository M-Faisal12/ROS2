import rclpy
from rclpy.node import Node

from my_robot_interfaces.msg  import Intent
from my_robot_interfaces.srv  import Schedule, Notes

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import speech_recognition as sr
import re

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

INTENTS = [
    "create_schedule",
    "query_schedule",
    "create_note",
    "query_notes",
    "query_daily_plan",
    "unknown"
]

intent_embeddings = model.encode(INTENTS)

def record_audio(filename="input.wav", seconds=5, fs=44100):
    print("\n Speak now...")

    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()

    audio = (audio * 32767).astype(np.int16)
    write(filename, fs, audio)

    return filename


def speech_to_text(file):
    r = sr.Recognizer()

    with sr.AudioFile(file) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio)
    except:
        return None

def detect_intent(text):
    emb = model.encode(text)
    scores = util.cos_sim(emb, intent_embeddings)[0]

    idx = int(scores.argmax())
    confidence = float(scores[idx])

    return INTENTS[idx], confidence

def rule_override(text):
    t = text.lower()

    if "what's the plan" in t or "schedule today" in t:
        return "query_daily_plan"

    if any(k in t for k in ["meeting", "class", "at", "tomorrow", "today"]):
        return "create_schedule"

    if "note" in t:
        return "create_note"

    return None

class BrainNode(Node):

    def __init__(self):
        super().__init__("node1_brain")

        # Publisher
        self.pub = self.create_publisher(Intent, "intent_topic", 10)

        # Clients
        self.schedule_client = self.create_client(Schedule, "schedule_service")
        self.notes_client = self.create_client(Notes, "notes_service")

        self.get_logger().info(" Node1 Brain Running")

        self.run_loop()


    def call_schedule(self, req_type, time="", event=""):

        req = Schedule.Request()
        req.request_type = req_type
        req.time = time
        req.event = event

        future = self.schedule_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result().response


    def call_notes(self, req_type, note=""):

        req = Notes.Request()
        req.request_type = req_type
        req.note = note

        future = self.notes_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result().response

    def planner(self, text):

        intent, conf = detect_intent(text)
        rule = rule_override(text)

        if rule:
            intent = rule

        if intent == "create_schedule":
            return self.call_schedule("store", "8:00", text)

        elif intent == "query_schedule":
            return self.call_schedule("fetch")

        elif intent == "create_note":
            return self.call_notes("store", text)

        elif intent == "query_notes":
            return self.call_notes("fetch")

        elif intent == "query_daily_plan":
            s = self.call_schedule("fetch")
            n = self.call_notes("fetch")
            return f"Schedule: {s} | Notes: {n}"

        return "Unknown intent"

    def run_loop(self):

        while rclpy.ok():

            input("\n Press Enter to speak...")

            file = record_audio()
            text = speech_to_text(file)

            if not text:
                print(" Could not understand")
                continue

            print("\n YOU SAID:", text)

            result = self.planner(text)

            print("\n FINAL RESULT:", result)


def main():
    rclpy.init()
    node = BrainNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()