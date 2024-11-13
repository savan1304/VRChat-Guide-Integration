import io
import json
import os
import time
import wave
from distutils.log import Log

import ffmpeg
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from csvLogger import CSVLogger, LogElements
from playsound import playsound
from pydub import AudioSegment, silence
from scipy.io.wavfile import write
from vosk import KaldiRecognizer, Model

INPUT_DEVICE_INDEX = 1
OUTPUT_DEVICE_INDEX = 6
TEMP_FILE = "speech_check.wav"
MODEL_PATH = "./vosk-model/vosk-model-small-en-us-0.15"
AUDIO_CSV_LOGGER = ""


def convertAudio(fileName):
    stream = ffmpeg.input(fileName)
    stream = ffmpeg.output(stream, TEMP_FILE, acodec="pcm_s16le", ac=1, ar="16k")
    ffmpeg.run(stream, overwrite_output=True)


def isHumanSpeech(fileName):
    global AUDIO_CSV_LOGGER
    start = time.perf_counter()
    wf = wave.open(fileName, "rb")
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    result = json.loads(rec.FinalResult())
    if len(result.get("text")) > 0:
        end = time.perf_counter()
        detect_time = round(end - start, 2)
        AUDIO_CSV_LOGGER.set_enum(
            LogElements.TIME_FOR_HUMAN_SPEECH_RECOGNITION, detect_time
        )
        return True

    else:
        return False


# check silenceThreshold and maxSilenceLength
def recordAudio(fileName, silenceThreshold=-40, maxSilenceLength=1):
    fs = 16000  # Sample rate
    # fs = 44000  # Sample rate HACK
    CHUNK_SIZE = int(fs * 0.5)  # Record in chunks of 0.5 seconds

    audio_chunks = []
    silence_duration = 0

    print("Recording started... Speak something...")

    # HACK to find device number on linux, use sounddevice.query_devices() to find the id of mic (mine is 7)
    with sd.InputStream(samplerate=fs, channels=1) as stream:
        while True:
            audio_chunk, overflowed = stream.read(CHUNK_SIZE)

            # Convert numpy array to AudioSegment for pydub processing
            byte_io = io.BytesIO()
            write(byte_io, fs, audio_chunk)
            byte_io.seek(0)
            segment = AudioSegment.from_wav(byte_io)
            print("dBFS:", segment.dBFS)

            if segment.dBFS < silenceThreshold:
                silence_duration += CHUNK_SIZE / fs
                if silence_duration >= maxSilenceLength:
                    print("Silence detected, stopping recording.")
                    break
            else:
                silence_duration = 0
            audio_chunks.append(audio_chunk)

    recording = np.concatenate(audio_chunks, axis=0)

    write(fileName, fs, recording)
    convertAudio(fileName)
    if not isHumanSpeech(TEMP_FILE):
        print("Nothing recorded, speak again!")
        recordAudio(fileName)


def normalizeAudio(fileName):
    currSegment = AudioSegment.from_file(fileName)
    normalizeAudio = currSegment.normalize()
    normalizeAudio.export(fileName, format="wav")


def listenAndRecord(fileName, CSV_LOGGER: CSVLogger):
    global AUDIO_CSV_LOGGER
    AUDIO_CSV_LOGGER = CSV_LOGGER
    start = time.perf_counter()
    recordAudio(fileName)
    end = time.perf_counter()
    record_time = round(end - start, 2)
    AUDIO_CSV_LOGGER.set_enum(LogElements.TIME_FOR_AUDIO_RECORD, record_time)

    start = time.perf_counter()
    normalizeAudio(fileName)
    end = time.perf_counter()
    normalize_time = round(end - start, 2)
    AUDIO_CSV_LOGGER.set_enum(LogElements.TIME_FOR_VOICE_NORMALIZATION, normalize_time)

    listen = input("Do you want to listen the recorded audio? [y/n]")
    if listen.lower() == "y":
        playsound(fileName)


def deleteAudioFile(fileName):
    try:
        os.remove(fileName)
    except:
        return
