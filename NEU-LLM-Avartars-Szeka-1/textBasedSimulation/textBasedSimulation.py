from responseGenerator import *
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from retrievalFunction import retrievalFunction
from audioRecorder import listenAndRecord
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

load_dotenv()

# Constants
DATABASE_NAME = "LLMDatabase"
DATABASE_URL = os.environ.get("DATABASE_URL")
COLLECTION_USERS = "NPC Avatars"
COLLECTION_MEMORY_OBJECTS = "ev018"

MAX_DEQUE_LENGTH = 50

# Basic objects for the Database.
client = MongoClient(DATABASE_URL)
LLMdatabase = client[DATABASE_NAME]
userCollection = LLMdatabase[COLLECTION_USERS]
memoryObjectCollection = LLMdatabase[COLLECTION_MEMORY_OBJECTS]


REFLECTION_RETRIEVAL_COUNT = 5
CHECK_REFLECTION_PERIOD = 5
CHECK_SATURATION_PEROID = 1
FILENAME = "current_conversation.wav"

all_conversations = []
CSV_LOGGER = CSVLogger()


def get_conversation_input(currMode, agent_mode, npc_name, conversationalUser, question_list, conversation_count):
    if currMode == CONVERSATION_MODE.TEXT.value:
        return text_conversation_input(agent_mode, npc_name, conversationalUser, question_list, conversation_count)
    elif currMode == CONVERSATION_MODE.AUDIO.value:
        return audio_conversation_input(CSV_LOGGER, FILENAME)


def text_conversation_input(agent_mode, userName, conversationalUser, question_list, conversation_count):
    start = time.perf_counter()
    if agent_mode == AGENT_MODE.RESEARCH.value:
        currentConversation = input(
            f"Talks with {userName}, You are {conversationalUser}. Talk about {RESEARCH_GOALS}! "
        )
    elif agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
        currentConversation = input(
            f"{question_list[conversation_count]} "
        )
    elif agent_mode == AGENT_MODE.DEBATE.value:
        currentConversation = input(
            f"Talk with {userName}, You are {conversationalUser}. Engage in a debate on {DEBATE_GOALS}! "
        )
    else:
        currentConversation = input(
            f"Talk with {userName}, You are {conversationalUser}. Have a discussion! "
        )

    end = time.perf_counter()
    text_input_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_FOR_INPUT, text_input_time)
    CSV_LOGGER.set_enum(LogElements.TIME_AUDIO_TO_TEXT, 0)

    return currentConversation


def audio_conversation_input(CSV_LOGGER, FILENAME):
    start = time.perf_counter()
    listenAndRecord(FILENAME, CSV_LOGGER)
    end = time.perf_counter()
    audio_record_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_FOR_INPUT, audio_record_time)

    start = time.perf_counter()
    currentConversation = getTextfromAudio(FILENAME)
    end = time.perf_counter()
    audio_to_text_time = round(end - start, 2)
    CSV_LOGGER.set_enum(LogElements.TIME_AUDIO_TO_TEXT, audio_to_text_time)

    return currentConversation


def startConversation(npc_name, currMode, agent_mode):
    global pastObservations, all_conversations

    conversationalUser = get_conversational_user(agent_mode=agent_mode)
    baseObservation = fetchBaseDescription(npc_name)
    pastObservations = fetchPastRecords(conversationalUser)
    eventLoop = asyncio.get_event_loop()
    threadExecutor = ThreadPoolExecutor()

    conversation_count = 0
    question_list = generate_interview_questions_list(agent_mode, RESEARCH_GOALS, INTERVIEW_ROUNDS)
    print(f"Starting conversation with {npc_name} as {conversationalUser}...\n")

    while True:
        current_conversation_str = ""
        is_question_event_agent=False

        currentConversation = get_conversation_input(currMode, agent_mode, npc_name, conversationalUser, question_list, conversation_count)
        CSV_LOGGER.set_enum(LogElements.MESSAGE, currentConversation)

        if currentConversation.lower() == "done":
            break

        if agent_mode != AGENT_MODE.EVENT.value:
            current_conversation_str += f"User: {currentConversation}. "
        elif agent_mode == AGENT_MODE.EVENT.value:
            is_question_event_agent = is_question_function(currentConversation)
            if not is_question_event_agent:
                current_conversation_str += f"{currentConversation}. "

        baseRetrieval, observationRetrieval, retrieval_time = perform_observation_retrieval(
            agent_mode, currentConversation, baseObservation, pastObservations
        )
        CSV_LOGGER.set_enum(LogElements.TIME_RETRIEVAL, retrieval_time)

        important_observations = select_important_observations(agent_mode, baseRetrieval, observationRetrieval)
        # print(f"Important Observations: {important_observations}")
        CSV_LOGGER.set_enum(LogElements.IMPORTANT_OBSERVATIONS, "\n".join(important_observations))

        important_scores = calculate_important_scores(agent_mode, baseRetrieval, observationRetrieval)
        CSV_LOGGER.set_enum(LogElements.IMPORTANT_SCORES, "\n".join(map(str, important_scores)))

        if agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
            resultConversationString = question_list[conversation_count]
        else:
            start = time.perf_counter()
            conversationPrompt = generate_conversation_helper( npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode, is_question=is_question_event_agent, )
            end = time.perf_counter()
            npc_response_time = round(end - start, 2)

            print(f"{npc_name} :")
            resultConversationString = ""
            for conversation in conversationPrompt:
                try:
                    currText = conversation.choices[0].delta.content
                    resultConversationString += currText
                    print(currText, end="")
                except:
                    break
            
            CSV_LOGGER.set_enum(LogElements.TIME_FOR_RESPONSE, npc_response_time)
            filtered_result = filter_conversation(resultConversationString)
            if agent_mode != AGENT_MODE.EVENT.value:
                current_conversation_str += f"NPC: {filtered_result}.\n"
            print(f"Time taken for the conversation generation by GPT : {npc_response_time}" )
        CSV_LOGGER.set_enum(LogElements.NPC_RESPONSE, resultConversationString)

            
        start = time.perf_counter()
        if not is_question_event_agent:
            eventLoop.run_in_executor( threadExecutor, generateObservationAndUpdateMemory, npc_name, conversationalUser, currentConversation, resultConversationString, current_conversation_str)
        end = time.perf_counter()
        generate_observation_time = round(end - start, 2)
        CSV_LOGGER.set_enum(LogElements.TIME_FOR_GENERATE_OBS, generate_observation_time)
        all_conversations.append(current_conversation_str)

        conversation_count += 1

        if conversation_count != 1 and conversation_count % CHECK_REFLECTION_PERIOD == 0 and agent_mode == AGENT_MODE.NORMAL.value:
            start = time.perf_counter()
            eventLoop.run_in_executor(threadExecutor, perform_reflection_logic, npc_name, conversationalUser, currentConversation, pastObservations)
            end = time.perf_counter()
            reflection_time = round(end - start, 2)
            CSV_LOGGER.set_enum(LogElements.TIME_FOR_REFLECTION, reflection_time)
        
        if conversation_count != 1 and conversation_count % CHECK_SATURATION_PEROID == 0:
            start = time.perf_counter() 
            is_saturation = check_saturation(npc_name, conversationalUser, all_conversations)
            end = time.perf_counter()
            saturation_check_time = round(end - start, 2)
            print(f"Time taken for the saturation check : {saturation_check_time}" )

            if is_saturation:
                bullet_points_response = get_bullet_points_response(conversationalUser, all_conversations)
                saturation_check_response = input(
                    f"{bullet_points_response} "
                )
                intention_response = check_saturation(npc_name, conversationalUser,saturation_check_response)
                if intention_response:
                    print("Conversation ended due to saturation.")
                    break
 
        if conversation_count == INTERVIEW_ROUNDS and agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
            print("Conversation ended due to interview rounds.")
            break

        CSV_LOGGER.write_to_csv(True) # write all values to csv


def fetchBaseDescription(userName: str):
    baseObservation = deque(
        memoryObjectCollection.find(
            {"Username": userName, "Conversation with User": "Base Description"}
        ),
    )
    if baseObservation:
        observation_dict = baseObservation[0]
        filtered_observations = [
            obs for obs in observation_dict['Observations'] if obs.strip()
        ]
        observation_dict['Observations'] = filtered_observations

    return baseObservation


def fetchPastRecords(userName: str):
    fetchQuery = {
        "$or": [{"Username": userName}, {"Conversation with User": userName}],
        "Conversation with User": {"$ne": "Base Description"},
    }
    return deque(
        memoryObjectCollection.find(fetchQuery).sort("_id", -1).limit(MAX_DEQUE_LENGTH), maxlen=MAX_DEQUE_LENGTH
    )


def update_reflection_db_and_past_obs(
        userName: str,
        conversationalUser: str,
        observationList: list
):
    global pastObservations
    # Get the current time.
    currTime = datetime.datetime.utcnow()
    # Update the memoryObjects collection.
    memoryObjectData = {
        "Username": userName,
        "Conversation with User": conversationalUser,
        "Creation Time": currTime,
        "Observations": observationList,
    }
    currentObject = memoryObjectCollection.insert_one(memoryObjectData)
    # Delete the oldest record and add the latest one.
    memoryObjectData["_id"] = currentObject.inserted_id
    # Delete the oldest record and add the latest one.
    if len(pastObservations) > MAX_DEQUE_LENGTH:
        pastObservations.pop()
    pastObservations.appendleft(memoryObjectData)


def updateBaseDescription(userName: str, observationList: list):
    # Get the current time.
    currTime = datetime.datetime.utcnow()
    # Update the memoryObjects collection.
    memoryObjectData = {
        "Username": userName,
        "Conversation with User": "Base Description",
        "Creation Time": currTime,
        "Observations": observationList,
    }
    # Update the latest collection with the id parameter and insert to the database.
    memoryObjectCollection.insert_one(memoryObjectData)
    # Delete the oldest record and add the latest one.


def update_Memory_Collection_and_past_obs(
    userName: str, conversationalUser: str, observationList: list
):
    global pastObservations
    # Get the current time.
    currTime = datetime.datetime.utcnow()
    # Update the memoryObjects collection.
    memoryObjectData = {
        "Username": userName,
        "Conversation with User": conversationalUser,
        "Creation Time": currTime,
        "Observations": observationList,
    }
    # Update the latest collection with the id parameter and insert to the database.
    currentObject = memoryObjectCollection.insert_one(memoryObjectData)
    memoryObjectData["_id"] = currentObject.inserted_id
    # Delete the oldest record and add the latest one.
    if len(pastObservations) > MAX_DEQUE_LENGTH:
        pastObservations.pop()
    pastObservations.appendleft(memoryObjectData)


def perform_reflection_logic(
    userName, conversationalUser, currentConversation, pastObservations,
):
    print("NPC in reflection...\n")
    reflection_retrieval = retrievalFunction(
        currentConversation=currentConversation,
        memoryStream=pastObservations,
        retrievalCount=REFLECTION_RETRIEVAL_COUNT,
        isBaseDescription=False,
        is_only_recency=True,
    )
    reflection_observations = [data[1] for data in reflection_retrieval]

    reflection_list = generate_reflection(
        userName,
        conversationalUser,
        pastConversations=reflection_observations,
    ).split("\n")
    finalObservations = []
    for observation in reflection_list:
        if len(observation) > 0:
            finalObservations.append(observation)
    # print(f"NPC reflection: {finalObservations}")
    update_reflection_db_and_past_obs(
        userName,
        conversationalUser,
        finalObservations
    )


def generateObservationAndUpdateMemory(
    userName,
    conversationalUser,
    currentConversation,
    resultConversationString,
    npc_dialogues
):
    # # Time the function call and fetch the results.
    # startTime = time.perf_counter()
    # observationList = generateObservations(
    #     userName, conversationalUser, currentConversation, resultConversationString
    # )
    # observationList = observationList.split("\n")
    finalObservations = []
    finalObservations.append(npc_dialogues)
    # for observation in observationList:
    #     if len(observation) > 0:
    #         finalObservations.append(observation)

    # endTime = time.perf_counter()
    update_Memory_Collection_and_past_obs(
        userName, conversationalUser, finalObservations)





if __name__ == "__main__":
    currMode = setConversationMode()
    agent_mode = set_agent_mode()

    pastObservations = deque()
    npc_name = get_npc_name(agent_mode)

    # Check for existing user.
    is_existing_npc_in_user_collection = userCollection.find_one(
        {"Username": npc_name})

    if is_existing_npc_in_user_collection:
        # print(f"Welcome back! {npc_name} \nContinue where you left off")
        avatar_expression_map = is_existing_npc_in_user_collection[
            AVATAR_DATA.AVATAR_EXPRESSION_MAP.value]
        avatar_action_map = is_existing_npc_in_user_collection[AVATAR_DATA.AVATAR_ACTION_MAP.value]
        avatar_voice = is_existing_npc_in_user_collection[AVATAR_DATA.AVATAR_VOICE.value]
        avatar_expressions = list(avatar_expression_map.keys())
        avatar_actions = list(avatar_action_map.keys())
    else:
        description = getBaseDescription(agent_mode)
        # Insert the userData to the Users collection.
        userData = {
            "Username": npc_name,
            "Description": description,
            "Avatar Expressions Map": avatar_expression_map,
            "Avatar Actions Map": avatar_action_map,
            "Avatar Voice": avatar_voice,
        }
        userCollection.insert_one(userData)
        # Time the function call and fetch the results.
        startTime = time.time()
        observationList = generateInitialObservations(
            npc_name, description).split("\n")
        endTime = time.time()
        print(
            f"Time taken for the observation generation by GPT : {endTime-startTime:.2f} "
        )

        # Generate the memory object data and push it to the memory objects collection.
        updateBaseDescription(npc_name, observationList)
        print("User created successfully!")
        print(f"Welcome back! {npc_name} \nContinue where you left off")
        avatar_expressions = list(avatar_expression_map.keys())
        avatar_actions = list(avatar_action_map.keys())

    startConversation(npc_name, currMode, agent_mode)

    summirzation_response = get_summurization_response(npc_name, all_conversations)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"./evaluations/summarization_response_{timestamp}.txt"
    write_to_file(summirzation_response, filename)
    # print(f"Summarization response: {summirzation_response}")
    client.close()
