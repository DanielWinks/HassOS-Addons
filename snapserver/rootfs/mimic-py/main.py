#!/usr/bin/python3
"""Creates TTS file and plays to Snapcast FIFO"""
from subprocess import DEVNULL, PIPE, Popen

from flask import Flask, Response, jsonify, make_response, request

app = Flask(__name__)


def join_wav() -> int:
    """Pads TTS message with leading second of silence."""
    cmd = ["sox", "alertklaxon_clean", "tts.wav", "output_tts.wav"]
    sox_proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
    return sox_proc.wait()


def get_tts(message: str) -> int:
    """Creates TTS message."""
    output = "tts.wav"
    mimic_proc = Popen(
        ["mimic", "-t", message, "-o", output],
        stdout=PIPE,
        stderr=DEVNULL,
    )
    return mimic_proc.wait()


def play_tts(fifo: str) -> int:
    """Creates TTS message."""
    pipeline = f"filesrc location=/output_tts.wav ! decodebin ! audioresample ! audioconvert ! audio/x-raw,rate=48000,channels=2,format=S16LE ! wavenc ! filesink location={fifo}"
    cmd = pipeline.split(" ")
    cmd.insert(0, "gst-launch-1.0")

    gst_launch_proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
    return gst_launch_proc.wait()


@app.route("/tts", methods=["POST"])
def tts() -> Response:
    error = {"message": "NOK", "code": "FAILURE"}
    success = {"message": "OK", "code": "SUCCESS"}

    request_data = request.get_json()
    message = request_data["message"]
    if get_tts(message) > 0:
        return make_response(jsonify(error), 500)

    if join_wav() > 0:
        return make_response(jsonify(error), 500)

    fifo = request_data["fifo"]
    if play_tts(fifo) > 1:
        return make_response(jsonify(error), 500)

    return make_response(jsonify(success), 200)


@app.route("/health", methods=["GET"])
def health() -> Response:
    """Responder for get requests."""
    data = {"message": "OK", "code": "SUCCESS"}
    return make_response(jsonify(data), 200)


if __name__ == "__main__":
    app.run()
