# Summary of the current changes as part of integraqtion effort:
# Updated movement descriptions to reflect guiding behavior
# Maintained core expression and movement functionality
# Optimized random actions for world/feature demonstrations

import os
from dotenv import load_dotenv
import re
load_dotenv()
import random
import VRC_OSCLib
import time
GPT4='gpt-4'
GPT35='gpt-3.5-turbo'
API_KEY=os.environ.get('API_KEY')


# integration effort
def generate_random_action(client):
    while(1):
        rand_action=random.randint(1, 8)
        if rand_action==1:
            # Guide showing points of interest
            VRC_OSCLib.acitonLook_left(client, 2)
            print("guide movement--looking at feature")
        elif rand_action==2:
            VRC_OSCLib.acitonLook_right(client,2)
            print("guide movement--indicating direction")
        elif rand_action==3:
            VRC_OSCLib.acitonMove(client,"forward", 0.2 ,False)
            print("guide movement--leading the way")
        elif rand_action==4:
            VRC_OSCLib.acitonMove(client, "backward", 0.2, False)
            print("guide movement--showing space")
        elif rand_action==5:
            VRC_OSCLib.acitonMove(client, "left", 0.2, False)
            print("guide movement--exploring left")
        elif rand_action == 6:
            VRC_OSCLib.acitonMove(client, "right", 0.2, False)
            print("guide movement--exploring right")
        elif rand_action==7:
            VRC_OSCLib.acitonJump(client)
            print("guide movement--highlighting feature")
        else:
            print("standing still for explanation")
        time.sleep(5)




# def generate_random_action(client):
#     while(1):
#         rand_action=random.randint(1, 8)
#         if rand_action==1:
#         #look left
#             VRC_OSCLib.acitonLook_left(client, 2)
#             print("random move--acitonLook_left")
#         elif rand_action==2:
#         # look right
#             VRC_OSCLib.acitonLook_right(client,2)
#             print("random move--acitonLook_right")
#         elif rand_action==3:
#         # walk forward
#             VRC_OSCLib.acitonMove(client,"forward", 0.2 ,False)
#             print("random move--acitonMove_forward")
#         elif rand_action==4:
#         # walk backward
#             VRC_OSCLib.acitonMove(client, "backward", 0.2, False)
#             print("random move--acitonMove_backward")
#         elif rand_action==5:
#         # walk left
#             VRC_OSCLib.acitonMove(client, "left", 0.2, False)
#             print("random move--acitonMove_left")
#         elif rand_action == 6:
#         # walk right
#             VRC_OSCLib.acitonMove(client, "right", 0.2, False)
#             print("random move--acitonMove_right")
#         elif rand_action==7:
#         # jump
#             VRC_OSCLib.acitonJump(client)
#             print("random move--jump")
#         else:
#             print("no movements")
#         time.sleep(5)


# parsing emotion tags
# integration effort
def extract_emotions(text):
    matches = re.findall(r'\((.*?)\)', text)
    valid_expressions = ["Happy", "Excited", "Confused", "Tease", "Wink", "Sad"]
    return [m for m in matches if m in valid_expressions]


#  cleaning text
def remove_emotions_from_string(conversation_string):
    # Replace patterns like (Smug, Dance) with an empty string
    cleaned_string = re.sub(r"\(.*?\)", "", conversation_string).strip()
    return cleaned_string