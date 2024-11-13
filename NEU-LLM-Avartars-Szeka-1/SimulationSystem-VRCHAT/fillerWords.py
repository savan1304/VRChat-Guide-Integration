# Summary of the current changes as part of integraqtion effort:

# 1. Filler Dictionaries:
#   How: Updated all filler text to focus on VRChat guidance
#   Why: Makes responses more relevant to world/feature recommendations
# 
# 2. Audio Generation:
#   How: Kept OpenAI TTS integration
#   Why: Provides high-quality voice output for guide responses
# 
# 3. Threading:
#   How: Maintained thread-safe audio handling
#   Why: Ensures smooth audio playback during interactions


import soundfile
from pydub import AudioSegment
from openai import OpenAI
import os
from dotenv import load_dotenv
import threading
import sounddevice
import configparser
import contextlib
import importlib
import re
import threading
from os import getenv
from pathlib import Path
import numpy as np
import boto3
import botocore
import botocore.exceptions
import sounddevice
import soundfile
import numpy as np
import io
import time
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
CURRENT_FRAME = 0
event = threading.Event()
playback_lock = threading.Lock()
load_dotenv()
import os
class Polly:
    """Use Amazon Polly API to synthesize a speech.

    This class can be used as speech_provider attribute for the VRCSpeechAssistant class.

    Attributes
    ----------
    AWS_CONFIG_FILE: Path
        Default location of Amazon AWS API config file.
    AWS_CREDENTIALS_FILE: Path
        Default location of Amazon AWS API credentials file.
    VOICES_PATH: Path
        The location of the voices files that will be generated.
    """

    AWS_CONFIG_FILE = Path.home() / ".aws" / "config"
    AWS_CREDENTIALS_FILE = Path.home() / ".aws" / "credentials"
    VOICES_PATH = Path(getenv("APPDATA")) / "VRChat LLM Avartars" / "voices"

    def __init__(self):
        """Initialize instance."""
        self.aws_config = configparser.ConfigParser()
        self.aws_credentials = configparser.ConfigParser()
        self._init_config()
        self.client = boto3.client("polly")
        # The first self.client.synthesize_speech called takes a little time to respond,
        # calling self.speech once before the user call it.
        self.speech("test", "Justin", 999)

    def _init_config(self):
        self._load_base_aws_config()
        if self.AWS_CONFIG_FILE.exists():
            self.aws_config.read(self.AWS_CONFIG_FILE)
        self.save_aws_config()
        self._load_base_aws_credentials()
        if self.AWS_CREDENTIALS_FILE.exists():
            self.aws_credentials.read(self.AWS_CREDENTIALS_FILE)
        self.save_aws_credentials()

    def _load_base_aws_config(self):
        self.aws_config["default"] = {"region": "us-west-2"}

    def _load_base_aws_credentials(self):
        self.aws_credentials["default"] = {
            "aws_access_key_id": "{aws_access_key_id}",
            "aws_secret_access_key": "{aws_secret_access_key}",
        }

    def save_aws_config(self):
        """Save aws configuration changes to the aws configuration file."""
        self.AWS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.aws_config.write(self.AWS_CONFIG_FILE.open("w", encoding="utf-8"))

    def save_aws_credentials(self):
        """Save aws credentials changes to the aws credentials file."""
        self.AWS_CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.aws_credentials.write(self.AWS_CREDENTIALS_FILE.open("w", encoding="utf-8"))

    def speech(self, text: str, voice_id: str, output_device_index: int, extra_tags: dict = None):


        """Convert a text into a speech and then play it to the given output_device.

        Parameters
        ----------
        text : str
            The text to be converted to speech.
        voice_id : str
            The voice id of the voice you want to use.
        output_device_index : int
            The index of the output device.
        extra_tags : dict
            A dict of extra tags. Currently only {"Whispered": bool} available.
        """

        def convert_to_ssml(input_text):
            # https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html
            if extra_tags and extra_tags.get("whispered"):
                return (
                    "<speak>"
                    + '<amazon:auto-breaths frequency="low" volume="soft" duration="x-short">'
                    + '<amazon:effect name="whispered">'
                    + input_text
                    + "</amazon:effect>"
                    + "</amazon:auto-breaths>"
                    + "</speak>"
                )
            return (
                "<speak>"
                + '<amazon:auto-breaths frequency="low" volume="soft" duration="x-short">'
                + input_text
                + "</amazon:auto-breaths>"
                + "</speak>"
            )

        # # Remove special characters from the text for the file destination.
        filename = re.sub("[#<$+%>!`&*'|{?\"=/}:@]", "", text)
        print(self.VOICES_PATH / voice_id / f"w_{filename}.ogg")
        if extra_tags and extra_tags.get("whispered"):
            filepath = self.VOICES_PATH / voice_id / f"w_{filename}.ogg"
        else:
            filepath = self.VOICES_PATH / voice_id / f"{filename}.ogg"
        # It creates the directory if it doesn't exist.
        filepath.parent.mkdir(parents=True, exist_ok=True)
        # Create the answer from Amazon Polly if the file does not exist.
        # if not filepath.exists():
        if not filepath.exists():
            try:
                response = self.client.synthesize_speech(
                    Text=convert_to_ssml(text),
                    VoiceId=voice_id.split(" ")[0],
                    OutputFormat="ogg_vorbis",
                    TextType="ssml",
                )
            except botocore.exceptions.ClientError as err:
                error(err)
                return
            with open(filepath, "wb") as file:
                file.write(response["AudioStream"].read())


event = threading.Event()

# General Fillers Dictionary
# integration effort
fillers = {
    "filler1": "Let me tell you about this world...",
    "filler2": "There are some interesting features here...",
    "filler3": "I can recommend a few places...",
    "filler4": "Let me show you around..."
}


# Question-Related Fillers Dictionary
# integration effort
fillersQ = {
    "fillerQ1": "That's a great question about VRChat...",
    "fillerQ2": "I know just the world for that...",
    "fillerQ3": "Let me help you find what you're looking for...",
    "fillerQ4": "I can guide you through that..."
}

# fillersQ = {
#     "fillerQ1": "Well, that's an interesting question, you see...",
#     "fillerQ2": "You know, that's a really good question. Let's see...",
#     "fillerQ3": "That's a thought-provoking question. To delve into it...",
#     "fillerQ4": "Indeed, that's a significant query. To address it...",
#     "fillerQ5": "That's a very insightful question. To tackle it head-on...",
#     "fillerQ6": "You've asked a pivotal question. To get to the heart of it...",
#     "fillerQ7": "That's a challenging question. To dissect it...",
#     "fillerQ8": "You raise an important point. To delve into the details...",
#     "fillerQ9": "That's a profound question, indeed. To explore it...",
#     "fillerQ10": "You've touched on a key issue. To examine it closely...",
#     "fillerQ11": "That's an intriguing question. To look at it from all angles...",
#     "fillerQ12": "You've posed a complex question. To unwrap it...",
#     "fillerQ13": "That's a critical question to consider. To break it down...",
#     "fillerQ14": "You've asked a pivotal query. To get to the core of it...",
#     "fillerQ15": "That's a substantial question. To analyze it...",
#     "fillerQ16": "You pose a thought-provoking question. To dive deeper...",
#     "fillerQ17": "That's a multifaceted question. To explore its depths...",
#     "fillerQ18": "You've raised a vital point. To scrutinize it...",
#     "fillerQ19": "That's a deep question, indeed. To look at it comprehensively...",
#     "fillerQ20": "You've highlighted a crucial issue. To dissect its layers...",
#     "fillerQ21": "That's a significant question to ponder. To examine its facets...",
#     "fillerQ22": "You ask a compelling question. To navigate through it...",
#     "fillerQ23": "That's a detailed question. To sift through the specifics...",
#     "fillerQ24": "You've posed an intriguing query. To explore its nuances...",
#     "fillerQ25": "That's a vital question to address. To analyze its components...",
#     "fillerQ26": "You raise a fundamental issue. To look at it in depth..."
# }





# Short Fillers Dictionary
# integration effort
fillersS = {
    "fillerS1": "hmm...let's see...",
    "fillerS2": "just a moment...",
    "fillerS3": "checking worlds...",
    "fillerS4": "finding options..."
}

# fillersS = {
#     "fillerS1": "umm...well...umm...",
#     "fillerS2": "uhh...Okay...uhh..",
#     "fillerS3": "erm...erm...alright..",
#     "fillerS4": "So...hmm...hmm...",
#     "fillerS5": "Hmm...Yes, well...",
#     "fillerS6": "Ah...Indeed...Ah...",
#     "fillerS7": "Right...Okay...So...",
#     "fillerS8": "Well...Yes...Hmm...",
#     "fillerS9": "Okay...Right...Well...",
#     "fillerS10": "So...Ah...Indeed...",
#     "fillerS11": "Yes...Hmm...Right...",
#     "fillerS12": "Ah...So...Okay...",
#     "fillerS13": "Well...Ah...Yes...",
#     "fillerS14": "Okay...So...Hmm...",
#     "fillerS15": "Hmm...Right...Ah...",
#     "fillerS16": "Yes...So...Okay...",
#     "fillerS17": "Right...Well...Ah...",
#     "fillerS18": "Ah...Hmm...Yes...",
#     "fillerS19": "So...Okay...Right...",
#     "fillerS20": "Hmm...Ah...So...",
#     "fillerS21": "Okay...Yes...Well...",
#     "fillerS22": "Yes...Ah...So...",
#     "fillerS23": "Right...Hmm...Okay...",
#     "fillerS24": "Ah...Well...Yes...",
#     "fillerS25": "So...Hmm...Right...",
#     "fillerS26": "Hmm...Okay...Yes...",
#     "fillerS27": "Yes...Right...Ah...",
#     "fillerS28": "Well...So...Hmm...",
#     "fillerS29": "Okay...Ah...Right...",
#     "fillerS30": "Hmm...Yes...So...",
#     "fillerS31": "Ah...Okay...Right...",
#     "fillerS32": "Right...Yes...Ah...",
#     "fillerS33": "Well...Hmm...Okay...",
#     "fillerS34": "Okay...So...Yes...",
#     "fillerS35": "So...Right...Ah...",
#     "fillerS36": "Yes...Hmm...Okay...",
#     "fillerS37": "Ah...So...Well...",
#     "fillerS38": "Right...Okay...Yes...",
#     "fillerS39": "Well...Ah...So...",
#     "fillerS40": "Okay...Hmm...Right...",
#     "fillerS41": "So...Yes...Ah...",
#     "fillerS42": "Yes...Okay...Well...",
#     "fillerS43": "Ah...Right...So...",
#     "fillerS44": "Right...Well...Hmm...",
#     "fillerS45": "Well...Okay...Ah...",
#     "fillerS46": "Okay...So...Hmm...",
#     "fillerS47": "So...Ah...Right...",
#     "fillerS48": "Yes...Well...Okay...",
#     "fillerS49": "Ah...Hmm...So...",
#     "fillerS50": "Right...Ah...Yes..."
# }




fillersG = {
    "fillerG1": "Hey there!",
    "fillerG2": "Hello, nice weather we're having, huh?",
    "fillerG3": "Hello, How's it going?",
    "fillerG4": "Hello!",
    "fillerG7": "Hello, Isn't this place just wonderful?",
    "fillerG8": "Hello, What a pleasant surprise to run into you!",
    "fillerG9": "Hey, it's great to see a friendly face!",
}


# integration effort
fillersA = {
    "fillerA1": "I found something...",
    "fillerA2": "Here's what I know...",
    "fillerA3": "Let me explain..."
}

# fillersA={
#     "fillerA1": "Oh..okay",
#     "fillerA2": "I see..",
#     "fillerA3": "ahh..",
# }

def generateAudio(text, filler):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    response.stream_to_file("TTS/fillerWord/"+filler+".mp3")
    AudioSegment.from_file("TTS/fillerWord/"+filler+".mp3").export("TTS/fillerWord/"+filler+".ogg", format="ogg")
    if os.path.exists("TTS/fillerWord/"+filler+".mp3"):
        os.remove("TTS/fillerWord/"+filler+".mp3")
        print(".mp3 file deleted")

load_dotenv()
API_KEY = os.environ.get("API_KEY")
client = OpenAI()
CURRENT_FRAME = 0

response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="Hello world! This is a streaming test.",
    response_format="mp3",
)

# # # Iterate over each item in the dictionary
# for key, value in fillers.items():
#     # Here 'key' is the filler identifier (like 'filler1', 'filler2', etc.)
#     # and 'value' is the corresponding filler text.
#     generateAudio(value, key)
#     print(f"{key}: {value}")
# for key, value in fillersQ.items():
#     # Here 'key' is the filler identifier (like 'filler1', 'filler2', etc.)
#     # and 'value' is the corresponding filler text.
#     generateAudio(value, key)
#     print(f"{key}: {value}")
# tts = Polly()
# for key, value in fillersS.items():
#     # Here 'key' is the filler identifier (like 'filler1', 'filler2', etc.)
#     # and 'value' is the corresponding filler text.
#     # generateAudio(value, key)
#     tts.speech(value, "Joanna", 8)
#     print(f"{key}: {value}")

# for key, value in fillersA.items():
#     # Here 'key' is the filler identifier (like 'filler1', 'filler2', etc.)
#     # and 'value' is the corresponding filler text.
#     # generateAudio(value, key)
#     generateAudio(value, key)
#     print(f"{key}: {value}")