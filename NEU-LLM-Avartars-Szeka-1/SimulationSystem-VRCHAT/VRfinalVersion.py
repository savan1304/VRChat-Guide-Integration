# Summary of the current changes as part of integration effort:

# 1. Added GenieWorksheets Integration:
    # Imported necessary modules (Agent, SUQLKnowledgeBase, SUQLParser)
    # Initialized onboarding knowledge base with VRChat-specific tables
    # Set up the onboarding agent with VRChat guidance focus

# 2. Updated Database Configuration:
    # Changed database names and collections to reflect VRChat focus
    # Switched from "LLMDatabase" to "vrchat_guide"
    # Updated collections for VRChat users and interactions

# 3. Kept Essential VRChat Integration:
    # Maintained all audio handling (filler, fillerShort, audio_conversation_input)
    # Preserved VRChat OSC communication
    # Kept avatar expression and action handling

# 4. Updated Conversation Logic:
    # Updated text_conversation_input for VRChat-specific prompts
    # Modified startConversation to use onboarding agent's response generation 
    # Maintained TTS and chat display functionality

# 5.  Removed Language Learning Components:
    # Commented out reflection system
    # Removed memory tracking
    # Eliminated observation generation
    # Removed conversation history tracking


from responseGenerator import *
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from retrievalFunction import retrievalFunction
from audioRecorder import listenAndRecordDirect, deleteAudioFile, check_audio_devices
from csvLogger import CSVLogger, LogElements
from collections import deque
from avatar_data import avatar_action_map, avatar_expression_map, avatar_voice
import datetime
import os
from dotenv import load_dotenv
from collections import deque
from pymongo.mongo_client import MongoClient
from dialoge_helper import *
from enums import CONVERSATION_MODE, AGENT_MODE, AVATAR_DATA
from dialoge_helper import get_npc_name
import VRC_OSCLib
import argparse
from pythonosc import udp_client
import random
import fillerWords
from TTS import openaiTTS, audio_device
from TTS import Polly
from STT import deepgramSTT
import controlexpression
import threading
load_dotenv()

# integration effort
# onboarding agent imports
from worksheets.agent import Agent
from worksheets.knowledge import SUQLKnowledgeBase, SUQLParser

from worksheets.runtime import GenieRuntime
from worksheets.context import GenieContext
from worksheets.chat import generate_next_turn

# Onboarding agent imports
from worksheets.chat import generate_next_turn
from worksheets.agent import Agent
from worksheets.knowledge import SUQLKnowledgeBase, SUQLParser


# integration effort
# onboarding agent imports
FILENAME = "./speech/current_conversation.wav"
Virtual_MIC_Channel = audio_device.get_vbcable_devices_info().cable_c_input.id
CSV_LOGGER = CSVLogger()

# VRC client setup
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=9000, help="The port the OSC server is listening on")
parser.add_argument("--use_cable_d", action="store_true", help="Use CABLE-D as the input device")
args = parser.parse_args()
VRCclient = udp_client.SimpleUDPClient(args.ip, args.port)


# integration effort (not needed for VRChat onboarding agent, but not sure whether to remove or not)
DATABASE_NAME = "vrchat_guide"  # Changed from LLMDatabase
DATABASE_URL = os.environ.get("DATABASE_URL")
COLLECTION_USERS = "VRChat Users"  # Changed from NPC Avatars
COLLECTION_MEMORY_OBJECTS = "vrchat_interactions"  # Changed from ev018
MAX_DEQUE_LENGTH = 50

# integration effort
# # Initialize onboarding agent
# onboarding_knowledge = SUQLKnowledgeBase(
#     llm_model_name="gpt-4",
#     tables_with_primary_keys={"vrchat_worlds": "id", "vrchat_events": "id"},
#     database_name="vrchat_guide"
# )

# # do not pass onboarding_knowledge to the parser
# onboarding_parser = SUQLParser(
#     llm_model_name="gpt-4",
#     knowledge=onboarding_knowledge
# )

# # Create runtime
# bot = GenieRuntime(
#     name="VRChatGuide",
#     prompt_dir="prompts/onboarding",
#     description="You are a VRChat guide helping users discover worlds and events, providing recommendations and assistance with VRChat features.",
#     knowledge_base=onboarding_knowledge,
#     knowledge_parser=onboarding_parser
# )

# # Load worksheets
# bot = bot.load_from_gsheet(gsheet_id="1aLyf6kkOpKYTrnvI92kHdLVip1ENCEW5aTuoSZWy2fU")

# onboarding_knowledge = SUQLKnowledgeBase(
#     llm_model_name="gpt-4",
#     tables_with_primary_keys={"vrchat_worlds": "id", "vrchat_events": "id"},
#     database_name="vrchat_guide"
# )

# # integration effort
# onboarding_parser = SUQLParser(
#     llm_model_name="gpt-4",
#     knowledge=onboarding_knowledge
# )

# # integration effort
# onboarding_agent = Agent(
#     botname="VRChatGuide",
#     description="You are a VRChat guide helping users discover worlds and events, providing recommendations and assistance with VRChat features.",
#     prompt_dir="prompts/onboarding",
#     knowledge_base=onboarding_knowledge,
#     knowledge_parser=onboarding_parser
# ).load_from_gsheet(gsheet_id="1aLyf6kkOpKYTrnvI92kHdLVip1ENCEW5aTuoSZWy2fU")


# # integration effort
# FILENAME = "./speech/current_conversation.wav"
# # CABLE-C Input
# Virtual_MIC_Channel = audio_device.get_vbcable_devices_info().cable_c_input.id
# CSV_LOGGER = CSVLogger()

# #VRC client
# parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="127.0.0.1",
#                         help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=9000,
#                         help="The port the OSC server is listening on")

# parser.add_argument("--use_cable_d", action="store_true",
#                     help="Use CABLE-D as the input device")
# args = parser.parse_args()
# VRCclient = udp_client.SimpleUDPClient(args.ip, args.port)
# load_dotenv()

# Not needed for VRChat onboarding agent - legacy database configuration
# DATABASE_NAME = "LLMDatabase"
# DATABASE_URL = os.environ.get("DATABASE_URL")
# COLLECTION_USERS = "NPC Avatars"
# COLLECTION_MEMORY_OBJECTS = "ev018"
# MAX_DEQUE_LENGTH = 50

# # Basic objects for the Database.
# client = MongoClient(DATABASE_URL)
# LLMdatabase = client[DATABASE_NAME]
# userCollection = LLMdatabase[COLLECTION_USERS]
# memoryObjectCollection = LLMdatabase[COLLECTION_MEMORY_OBJECTS]

# Not needed for VRChat onboarding agent - specific to language learning memory tracking
# REFLECTION_RETRIEVAL_COUNT = 5
# CHECK_REFLECTION_PERIOD = 5
# CHECK_SATURATION_PEROID = 5

# Not needed for VRChat onboarding agent - used for language learning conversation history
# all_conversations = []



# Initialize onboarding agent
onboarding_knowledge = SUQLKnowledgeBase(
    llm_model_name="gpt-4",
    tables_with_primary_keys={"vrchat_worlds": "id", "vrchat_events": "id"},
    database_name="vrchat_guide"
)

onboarding_parser = SUQLParser(
    llm_model_name="gpt-4",
    knowledge=onboarding_knowledge
)

onboarding_agent = Agent(
    botname="VRChatGuide",
    description="You are a VRChat guide helping users discover worlds and events, providing recommendations and assistance with VRChat features.",
    prompt_dir="prompts/onboarding",
    knowledge_base=onboarding_knowledge,
    knowledge_parser=onboarding_parser
).load_from_gsheet(gsheet_id="1aLyf6kkOpKYTrnvI92kHdLVip1ENCEW5aTuoSZWy2fU")


def filler(currentConversation):
    if "?" in currentConversation and len(currentConversation) > 40:
        selected_filler_key = random.choice(list(fillerWords.fillersQ.keys()))
        # VRC_OSCLib.actionChatbox(VRCclient, fillerWords.fillersQ[selected_filler_key])
        threading.Thread(target=VRC_OSCLib.actionChatbox,
                         args=(VRCclient, fillerWords.fillersQ[selected_filler_key],)).start()
        openaiTTS.read_audio_file("TTS/fillerWord/" + selected_filler_key + ".ogg", Virtual_MIC_Channel)

    else:
        selected_filler_key = random.choice(list(fillerWords.fillers.keys()))
        # VRC_OSCLib.actionChatbox(VRCclient, fillerWords.fillers[selected_filler_key])
        threading.Thread(target=VRC_OSCLib.actionChatbox,
                         args=(VRCclient, fillerWords.fillers[selected_filler_key],)).start()
        openaiTTS.read_audio_file("TTS/fillerWord/" + selected_filler_key + ".ogg", Virtual_MIC_Channel)


def fillerShort():
    selected_filler_key = random.choice(list(fillerWords.fillersS.keys()))
    threading.Thread(target=VRC_OSCLib.actionChatbox,
                     args=(VRCclient, fillerWords.fillersS[selected_filler_key],)).start()
    # VRC_OSCLib.actionChatbox(VRCclient, fillerWords.fillers[selected_filler_key])
    openaiTTS.read_audio_file("TTS/fillerWord/" + selected_filler_key + ".ogg", Virtual_MIC_Channel)



def audio_conversation_input(CSV_LOGGER, FILENAME):
    start = time.perf_counter()
    listenAndRecordDirect(CSV_LOGGER, FILENAME)
    threading.Thread(target=fillerShort, args=()).start()
    end = time.perf_counter()
    audio_record_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_FOR_INPUT, audio_record_time)

    start = time.perf_counter()
    currentConversation = getTextfromAudio_whisper_1(FILENAME)
    end = time.perf_counter()
    audio_to_text_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_AUDIO_TO_TEXT, audio_to_text_time)
    threading.Thread(target=filler, args=(currentConversation,)).start()
    deleteAudioFile(FILENAME)
    return currentConversation



def text_conversation_input(userName, conversationalUser):
    start = time.perf_counter()
    currentConversation = input(
        f"Talk with VRChat Guide about worlds, events, or features!"
    )
    end = time.perf_counter()
    text_input_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_FOR_INPUT, text_input_time)
    CSV_LOGGER.set_enum(LogElements.TIME_AUDIO_TO_TEXT, 0)
    return currentConversation



async def startConversation(currMode):

    # integration effort
    # audioRecorder.check_audio_devices()# VRC_OSCLib.actionChatbox(VRCclient, "Hi there! I'm your VRChat Guide. I can help you discover worlds, events, and features in VRChat. What would you like to know about?")

    STARTING_NOTIFICATION = "Hi there! I'm your VRChat Guide. I can help you discover worlds, events, and features in VRChat. What would you like to know about?"
    openaiTTS.generateAudio(STARTING_NOTIFICATION, Virtual_MIC_Channel)
    VRC_OSCLib.actionChatbox(VRCclient, STARTING_NOTIFICATION)

    # conversation_count = 0
    print("Starting VRChat Guide conversation...\n")

    while True:
        if currMode == CONVERSATION_MODE.TEXT.value:
            currentConversation = text_conversation_input("VRChatGuide", "User")
        elif currMode == CONVERSATION_MODE.AUDIO.value:
            currentConversation = audio_conversation_input(CSV_LOGGER, FILENAME)
        
        CSV_LOGGER.set_enum(LogElements.MESSAGE, currentConversation)

        if currentConversation.lower() == "done":
            break

        start = time.perf_counter()
        response = await generate_next_turn(currentConversation, onboarding_agent)
        resultConversationString = response.text
        end = time.perf_counter()
        npc_response_time = round(end - start, 2)

        print("VRChat Guide:")
        splitSentence = ""
        count = 0
        emotions = ""

        for currText in resultConversationString:
            try:
                splitSentence += currText
                if any(punct in currText for punct in ['.', '?', '!']):
                    if count == 0:
                        emotions = controlexpression.extract_emotions(splitSentence)
                        splitSentence = controlexpression.remove_emotions_from_string(splitSentence)
                        count += 1
                    print(splitSentence, end="")
                    openaiTTS.generateAudio(splitSentence, Virtual_MIC_Channel)
                    VRC_OSCLib.actionChatbox(VRCclient, splitSentence)
                    splitSentence = ""
            except:
                break

        if splitSentence:
            openaiTTS.generateAudio(splitSentence, Virtual_MIC_Channel)
            VRC_OSCLib.actionChatbox(VRCclient, splitSentence)
            print(splitSentence, end="")

        threading.Thread(target=VRC_OSCLib.send_expression_command, args=(emotions,)).start()
        CSV_LOGGER.set_enum(LogElements.NPC_RESPONSE, resultConversationString)
        CSV_LOGGER.set_enum(LogElements.TIME_FOR_RESPONSE, npc_response_time)
        CSV_LOGGER.write_to_csv(True)
        conversation_count += 1


# integration effort
# def fetchBaseDescription(userName: str):
#     baseObservation = deque(
#         memoryObjectCollection.find(
#             {"Username": userName, "Type": "VRChat Guide Base"}
#         ),
#     )
#     if baseObservation:
#         observation_dict = baseObservation[0]
#         filtered_observations = [
#             obs for obs in observation_dict['Observations'] if obs.strip()
#         ]
#         observation_dict['Observations'] = filtered_observations
#     return baseObservation


# integration effort
# def updateBaseDescription(userName: str, observationList: list):
#     currTime = datetime.datetime.utcnow()
#     memoryObjectData = {
#         "Username": userName,
#         "Type": "VRChat Guide Base",
#         "Creation Time": currTime,
#         "Observations": observationList,
#     }
#     memoryObjectCollection.insert_one(memoryObjectData)






# Not needed for VRChat onboarding agent - specific to language learning memory system
# def fetchPastRecords(userName: str):
#     fetchQuery = {
#         "$or": [{"Username": userName}, {"Conversation with User": userName}],
#         "Conversation with User": {"$ne": "Base Description"},
#     }
#     return deque(
#         memoryObjectCollection.find(fetchQuery).sort("_id", -1).limit(MAX_DEQUE_LENGTH), maxlen=MAX_DEQUE_LENGTH
#     )


# Not needed for VRChat onboarding agent - specific to language learning reflection system
# def update_reflection_db_and_past_obs(
#         userName: str,
#         conversationalUser: str,
#         observationList: list
#     ):
#     global pastObservations
#     # Get the current time.
#     currTime = datetime.datetime.utcnow()
#     # Update the memoryObjects collection.
#     memoryObjectData = {
#         "Username": userName,
#         "Conversation with User": conversationalUser,
#         "Creation Time": currTime,
#         "Observations": observationList,
#     }
#     currentObject = memoryObjectCollection.insert_one(memoryObjectData)
#     # Delete the oldest record and add the latest one.
#     memoryObjectData["_id"] = currentObject.inserted_id
#     # Delete the oldest record and add the latest one.
#     if len(pastObservations) > MAX_DEQUE_LENGTH:
#         pastObservations.pop()
#     pastObservations.appendleft(memoryObjectData)


# Not needed for VRChat onboarding agent - specific to language learning memory updates
# def update_Memory_Collection_and_past_obs(
#         userName: str, conversationalUser: str, observationList: list
#     ):
#     global pastObservations
#     # Get the current time.
#     currTime = datetime.datetime.utcnow()
#     # Update the memoryObjects collection.
#     memoryObjectData = {
#         "Username": userName,
#         "Conversation with User": conversationalUser,
#         "Creation Time": currTime,
#         "Observations": observationList,
#     }
#     # Update the latest collection with the id parameter and insert to the database.
#     currentObject = memoryObjectCollection.insert_one(memoryObjectData)
#     memoryObjectData["_id"] = currentObject.inserted_id
#     # Delete the oldest record and add the latest one.
#     if len(pastObservations) > MAX_DEQUE_LENGTH:
#         pastObservations.pop()
#     pastObservations.appendleft(memoryObjectData)


# Not needed for VRChat onboarding agent - specific to language learning reflection system
# def perform_reflection_logic(
#         userName, conversationalUser, currentConversation, pastObservations,
#     ):
#     print("NPC in reflection...\n")
#     reflection_retrieval = retrievalFunction(
#         currentConversation=currentConversation,
#         memoryStream=pastObservations,
#         retrievalCount=REFLECTION_RETRIEVAL_COUNT,
#         isBaseDescription=False,
#         is_only_recency=True,
#     )
#     reflection_observations = [data[1] for data in reflection_retrieval]

#     reflection_list = generate_reflection(
#         userName,
#         conversationalUser,
#         pastConversations=reflection_observations,
#     ).split("\n")
#     finalObservations = []
#     for observation in reflection_list:
#         if len(observation) > 0:
#             finalObservations.append(observation)
#     # print(f"NPC reflection: {finalObservations}")
#     update_reflection_db_and_past_obs(
#         userName,
#         conversationalUser,
#         finalObservations
#     )


# Not needed for VRChat onboarding agent - specific to language learning observation system
# def generateObservationAndUpdateMemory(
#         userName,
#         conversationalUser,
#         currentConversation,
#         resultConversationString,
#         npc_dialogues
#     ):
#     # # Time the function call and fetch the results.
#     # startTime = time.perf_counter()
#     # observationList = generateObservations(
#     #     userName, conversationalUser, currentConversation, resultConversationString
#     # )
#     # observationList = observationList.split("\n")
#     finalObservations = []
#     finalObservations.append(npc_dialogues)
#     # for observation in observationList:
#     #     if len(observation) > 0:
#     #         finalObservations.append(observation)

#     # endTime = time.perf_counter()
#     update_Memory_Collection_and_past_obs(
#         userName, conversationalUser, finalObservations)



if __name__ == "__main__":
    currMode = setConversationMode()
    
    # # Initialize VRChat Guide
    # if userCollection.find_one({"Username": "VRChatGuide"}):
    #     avatar_expression_map = userCollection.find_one({"Username": "VRChatGuide"})[
    #         AVATAR_DATA.AVATAR_EXPRESSION_MAP.value]
    #     avatar_action_map = userCollection.find_one({"Username": "VRChatGuide"})[
    #         AVATAR_DATA.AVATAR_ACTION_MAP.value]
    #     avatar_voice = userCollection.find_one({"Username": "VRChatGuide"})[
    #         AVATAR_DATA.AVATAR_VOICE.value]
    #     avatar_expressions = list(avatar_expression_map.keys())
    #     avatar_actions = list(avatar_action_map.keys())
    # else:
    #     userData = {
    #         "Username": "VRChatGuide",
    #         "Description": "VRChat Guide and World/Event Recommender",
    #         "Avatar Expressions Map": avatar_expression_map,
    #         "Avatar Actions Map": avatar_action_map,
    #         "Avatar Voice": avatar_voice,
    #     }
    #     userCollection.insert_one(userData)
    #     print("VRChat Guide initialized successfully!")
    #     avatar_expressions = list(avatar_expression_map.keys())
    #     avatar_actions = list(avatar_action_map.keys())

    asyncio.run(startConversation(currMode))
    # client.close()
