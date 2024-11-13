# Summary of the current changes as part of integration effort:

# 1. File Status:
#   How: Commented out entire file
#   Why: Using SimulationSystem-VRCHAT/csvLogger.py
# 
# 2. Integration Impact:
#   How: No changes needed
#   Why: Logging handled by VRChat implementation
# 
# 3. Dependencies:
#   How: Update imports in any referencing files
#   Why: Point to SimulationSystem-VRCHAT/csvLogger.py


# import csv
# import os
# from enum import Enum
# from datetime import datetime


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
#     TIME_FOR_SATURATION_CHECK = "Time for Saturation Check"

# class CSVLogger:
#     enum_values = {}
#     initialize_header = True
#     curr_time = datetime.now(tz=None)
#     curr_time = curr_time.strftime("%Y-%m-%d_%H-%M")
#     curr_file = f"./evaluations/TestScenarios_CSV/CSV_LOGS_{curr_time}.csv"

#     curr_file_dir = os.path.dirname(curr_file)
#     if not os.path.exists(curr_file_dir):
#         os.makedirs(curr_file_dir)

#     def set_enum(self, enum: Enum, result):
#         self.enum_values[enum.value] = result

#     def write_to_csv(self, log_values=True):
#         headers = [header.value for header in LogElements]
#         if log_values:
#             with open(self.curr_file, "a", newline="", encoding="utf-8") as csv_file:
#                 csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
#                 if self.initialize_header:
#                     csv_writer.writeheader()
#                     self.initialize_header = False
#                 csv_writer.writerow(self.enum_values)
