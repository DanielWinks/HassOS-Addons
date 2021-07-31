#!/usr/bin/python3
"""Creates TTS file and plays to Snapcast FIFO"""
import argparse
import io
import json
import os
import sys
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen
from typing import Union

from flask import Flask, Response, jsonify, make_response, render_template, request, send_file
from TTS.config import load_config
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

app = Flask(__name__)


def create_argparser():
    def convert_boolean(x):
        return x.lower() in ["true", "1", "yes"]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list_models",
        type=convert_boolean,
        nargs="?",
        const=True,
        default=False,
        help="list available pre-trained tts and vocoder models.",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="tts_models/en/ljspeech/tacotron2-DDC",
        help="Name of one of the pre-trained tts models in format <language>/<dataset>/<model_name>",
    )
    parser.add_argument(
        "--vocoder_name", type=str, default=None, help="name of one of the released vocoder models."
    )

    # Args for running custom models
    parser.add_argument("--config_path", default=None, type=str, help="Path to model config file.")
    parser.add_argument(
        "--model_path",
        type=str,
        default=None,
        help="Path to model file.",
    )
    parser.add_argument(
        "--vocoder_path",
        type=str,
        help="Path to vocoder model file. If it is not defined, model uses GL as vocoder. Please make sure that you installed vocoder library before (WaveRNN).",
        default=None,
    )
    parser.add_argument(
        "--vocoder_config_path", type=str, help="Path to vocoder model config file.", default=None
    )
    parser.add_argument(
        "--speakers_file_path", type=str, help="JSON file for multi-speaker model.", default=None
    )
    parser.add_argument("--port", type=int, default=5002, help="port to listen on.")
    parser.add_argument("--use_cuda", type=convert_boolean, default=False, help="true to use CUDA.")
    parser.add_argument(
        "--debug", type=convert_boolean, default=False, help="true to enable Flask debug mode."
    )
    parser.add_argument(
        "--show_details", type=convert_boolean, default=False, help="Generate model detail page."
    )
    return parser


# parse the args
args = create_argparser().parse_args()

path = Path(__file__).parent / "./.models.json"
manager = ModelManager(path)

if args.list_models:
    manager.list_models()
    sys.exit()

# update in-use models to the specified released models.
model_path = None
config_path = None
speakers_file_path = None
vocoder_path = None
vocoder_config_path = None

# CASE1: list pre-trained TTS models
if args.list_models:
    manager.list_models()
    sys.exit()

# CASE2: load pre-trained model paths
if args.model_name is not None and not args.model_path:
    model_path, config_path, model_item = manager.download_model(args.model_name)
    args.vocoder_name = (
        model_item["default_vocoder"] if args.vocoder_name is None else args.vocoder_name
    )

if args.vocoder_name is not None and not args.vocoder_path:
    vocoder_path, vocoder_config_path, _ = manager.download_model(args.vocoder_name)

# CASE3: set custome model paths
if args.model_path is not None:
    model_path = args.model_path
    config_path = args.config_path
    speakers_file_path = args.speakers_file_path

if args.vocoder_path is not None:
    vocoder_path = args.vocoder_path
    vocoder_config_path = args.vocoder_config_path

# load models
synthesizer = Synthesizer(
    model_path,
    config_path,
    speakers_file_path,
    vocoder_path,
    vocoder_config_path,
    use_cuda=args.use_cuda,
)

use_multi_speaker = (
    synthesizer.tts_model.speaker_manager is not None and synthesizer.tts_model.num_speakers > 1
)
speaker_manager = (
    synthesizer.tts_model.speaker_manager
    if hasattr(synthesizer.tts_model, "speaker_manager")
    else None
)
# TODO: set this from SpeakerManager
use_gst = synthesizer.tts_config.get("use_gst", False)
app = Flask(__name__)


def style_wav_uri_to_dict(style_wav: str) -> Union[str, dict]:
    """Transform an uri style_wav, in either a string (path to wav file to be use for style transfer)
    or a dict (gst tokens/values to be use for styling)
    Args:
        style_wav (str): uri
    Returns:
        Union[str, dict]: path to file (str) or gst style (dict)
    """
    if style_wav:
        if os.path.isfile(style_wav) and style_wav.endswith(".wav"):
            return style_wav  # style_wav is a .wav file located on the server

        style_wav = json.loads(style_wav)
        return style_wav  # style_wav is a gst dictionary with {token1_id : token1_weigth, ...}
    return None


def join_wav(wav: str) -> int:
    """Pads TTS message with prepended wav file."""
    cmd = ["sox", f"{wav}", "tts.wav", "output_tts.wav"]
    print("Joining wav files together using Sox")
    sox_proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
    return sox_proc.wait()


def play_tts(output_wav: str, fifo: str) -> int:
    """Creates TTS message."""
    pipeline = f"filesrc location=/{output_wav} ! decodebin ! audioresample ! audioconvert ! audio/x-raw,rate=48000,channels=2,format=S16LE ! wavenc ! filesink location={fifo}"
    cmd = pipeline.split(" ")
    cmd.insert(0, "gst-launch-1.0")

    gst_launch_proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
    return gst_launch_proc.wait()


@app.route("/")
def index():
    return render_template(
        "index.html",
        show_details=args.show_details,
        use_multi_speaker=use_multi_speaker,
        speaker_ids=speaker_manager.speaker_ids if speaker_manager is not None else None,
        use_gst=use_gst,
    )


@app.route("/details")
def details():
    model_config = load_config(args.tts_config)
    if args.vocoder_config is not None and os.path.isfile(args.vocoder_config):
        vocoder_config = load_config(args.vocoder_config)
    else:
        vocoder_config = None

    return render_template(
        "details.html",
        show_details=args.show_details,
        model_config=model_config,
        vocoder_config=vocoder_config,
        args=args.__dict__,
    )


@app.route("/tts", methods=["POST"])
def tts() -> Response:
    error = {"message": "NOK", "code": "FAILURE"}
    success = {"message": "OK", "code": "SUCCESS"}
    request.get_json(force=True)

    request_data = request.json
    text = request_data.pop("text")
    fifo = request_data.pop("fifo")
    speaker_idx = request_data.pop("speaker_id", "")
    style_wav = request_data.pop("style_wav", "")
    prepend_wav = request_data.pop("prepend_wav", "")
    print(f"{text}:{speaker_idx}:{style_wav}")

    style_wav = style_wav_uri_to_dict(style_wav)
    print(" > Model input: {}".format(text))
    wavs = synthesizer.tts(text, speaker_idx=speaker_idx, style_wav=style_wav)
    out = io.BytesIO()
    synthesizer.save_wav(wavs, out)
    with open("tts.wav", "wb") as outfile:
        outfile.write(out.getbuffer())

    if len(prepend_wav) > 0:
        if join_wav(prepend_wav) > 0:
            return make_response(jsonify(error), 500)

    if len(prepend_wav) > 0:
        if play_tts("output_tts.wav", fifo) > 1:
            return make_response(jsonify(error), 500)
    else:
        if play_tts("tts.wav", fifo) > 1:
            return make_response(jsonify(error), 500)

    return make_response(jsonify(success), 200)


@app.route("/api/tts", methods=["GET"])
def api_tts():
    text = request.args.get("text")
    speaker_idx = request.args.get("speaker_id", "")
    style_wav = request.args.get("style_wav", "")

    style_wav = style_wav_uri_to_dict(style_wav)
    print(" > Model input: {}".format(text))
    wavs = synthesizer.tts(text, speaker_idx=speaker_idx, style_wav=style_wav)
    out = io.BytesIO()
    synthesizer.save_wav(wavs, out)
    return send_file(out, mimetype="audio/wav")


@app.route("/health", methods=["GET"])
def health() -> Response:
    """Responder for get requests."""
    data = {"message": "OK", "code": "SUCCESS"}
    return make_response(jsonify(data), 200)


def main():
    app.run(debug=args.debug, host="::", port=args.port)


if __name__ == "__main__":
    main()
