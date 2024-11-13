# Summary of the current changes as part of integration effort:
# Simplified logging elements to focus on core interaction metrics
# Removed language learning specific logging elements
# Maintained essential timing and response tracking

import csv
import os
from enum import Enum
from datetime import datetime

# integration effort
class LogElements(Enum):
    MESSAGE = "Message"
    NPC_RESPONSE = "NPC Response"
    TIME_FOR_INPUT = "Total time for Input"
    TIME_FOR_HUMAN_SPEECH_RECOGNITION = "Time for Human speech detection"
    TIME_FOR_VOICE_NORMALIZATION = "Time for voice normalization"
    TIME_FOR_AUDIO_RECORD = "Time for audio recording"
    TIME_AUDIO_TO_TEXT = "Time for Audio to Text"
    TIME_FOR_RESPONSE = "Time for Response"

    # Not needed for VRChat onboarding agent - specific to language learning metrics
    # IMPORTANT_OBSERVATIONS = "Important Observations"
    # IMPORTANT_SCORES = "Important Scores"
    # TIME_FOR_REFLECTION = "Time for Reflection"
    # TIME_FOR_GENERATE_OBS = "Time for Generate Observations"
    # TIME_RETRIEVAL = "Time for Retrieval"


# class LogElements(Enum):
#     MESSAGE = "Message"
#     IMPORTANT_OBSERVATIONS = "Important Observations"
#     IMPORTANT_SCORES = "Important Scores"
#     NPC_RESPONSE = "NPC Response"
#     TIME_FOR_INPUT = "Total time for Input"
#     TIME_FOR_HUMAN_SPEECH_RECOGNITION = "Time for Human speech detection"
#     TIME_FOR_VOICE_NORMALIZATION = "Time for voice normalization"
#     TIME_FOR_AUDIO_RECORD = "Time for audio recording"
#     TIME_AUDIO_TO_TEXT = "Time for Audio to Text"
#     TIME_RETRIEVAL = "Time for Retrieval"
#     TIME_FOR_RESPONSE = "Time for Response"
#     TIME_FOR_REFLECTION = "Time for Reflection"
#     TIME_FOR_GENERATE_OBS = "Time for Generate Observations"




class CSVLogger:
    enum_values = {}
    initialize_header = True
    curr_time = datetime.now(tz=None)
    curr_time = curr_time.strftime("%Y-%m-%d_%H-%M")
    curr_file = f"evaluations\TestScenarios_CSV\CSV_LOGS_{curr_time}.csv"

    def set_enum(self, enum: Enum, result):
        self.enum_values[enum.value] = result

    def write_to_csv(self, log_values=True):
        # headers = [header.value for header in LogElements]

        # integration effort
        headers = [
            "Message",
            "NPC Response",
            "Total time for Input",
            "Time for Human speech detection",
            "Time for voice normalization", 
            "Time for audio recording",
            "Time for Audio to Text",
            "Time for Response"
        ]
        if log_values:
            with open(self.curr_file, "a", newline="", encoding="utf-8") as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
                if self.initialize_header:
                    csv_writer.writeheader()
                    self.initialize_header = False
                csv_writer.writerow(self.enum_values)