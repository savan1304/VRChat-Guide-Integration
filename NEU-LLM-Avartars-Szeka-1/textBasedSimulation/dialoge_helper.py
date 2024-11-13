from enums import CONVERSATION_MODE, AGENT_MODE
import re
from responseGenerator import generate_saturation_prompt, generate_summary_prompt, generateConversation, generate_interview_questions, generate_bullet_points_prompt
from retrievalFunction import retrievalFunction
import time

BASE_RETRIEVAL_COUNT = 3  # change parameter
OBS_RETRIEVAL_COUNT = 5  # change parameter
RA_RETRIVAL_COUNT = 5
EVENT_RETRIVAL_COUNT = 5
INTERVIEW_ROUNDS = 3

RESEARCH_GOALS = "experience in Vr chat, what activities they like doing in Vr chat and overall why do they value regarding VR chat?"
DEBATE_GOALS = "AI Agents should be included in VRChat in the future"


def get_conversational_user(agent_mode):
    """
    Determines the username based on the agent_mode.

    Parameters:
    - agent_mode: The mode of the agent which determines how the username is set.

    Returns:
    - A string representing the username to be used in conversations.
    """
    if agent_mode == AGENT_MODE.EVENT.value:
        conversationalUser = "User"
    else:
        conversationalUser = input("Define the username you are acting as: ")
    return conversationalUser


def get_npc_name(agent_mode):
    if agent_mode == AGENT_MODE.EVENT.value:
        return "Event Agent"
    elif agent_mode == AGENT_MODE.RESEARCH.value or agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
        return "Research Agent"
    elif agent_mode == AGENT_MODE.DEBATE.value:
        return "Debate Agent"
    else:
        return input("Please enter the username of character: ")


def is_question_function(message):
    question_keywords = ["what", "how", "where", "when", "why", "who", "?", ""]
    # Convert the message to lowercase for case-insensitive comparison
    message_lower = message.lower()

    for keyword in question_keywords:
        if keyword in message_lower:
            return True
    return False


def remove_numbers(question_list):
    processed_questions = []
    for question in question_list:
        # Find the index of the first non-digit character in the question
        index = 0
        for char in question:
            if not char.isdigit():
                break
            index += 1
        # Remove the numbers and any leading whitespace
        processed_question = question[index:].lstrip()
        processed_questions.append(processed_question)
    return processed_questions


def filter_conversation(conversation):
    # Remove text within parentheses
    filtered_result = re.sub(r'\([^()]*\)', '', conversation)
    # Remove newline characters
    filtered_result = filtered_result.replace('\n', '')
    return filtered_result


def setConversationMode():
    while True:
        currMode = input(
            "Please select the following :\n1. Text Mode\n2. Audio Mode\n")
        if currMode == "1":
            return CONVERSATION_MODE.TEXT.value
        elif currMode == "2":
            return CONVERSATION_MODE.AUDIO.value
        else:
            print("Invalid input, please select appropriate options")


def set_agent_mode():
    while True:
        user_input = input(
            "Select conversation mode:\n1. Normal Conversation\n2. Event Agent\n3. Interview Agent\n4. Debate Agent\n5. Predefined Interview\n6. AAC Mode \nEnter the corresponding number: ")
        if user_input == "1":
            return AGENT_MODE.NORMAL.value
        elif user_input == "2":
            return AGENT_MODE.EVENT.value
        elif user_input == "3":
            return AGENT_MODE.RESEARCH.value
        elif user_input == "4":
            return AGENT_MODE.DEBATE.value
        elif user_input == "5":
            return AGENT_MODE.PREDEFINED_RESEARCH.value
        elif user_input == "6":
            return AGENT_MODE.AAC.value
        else:
            print("Invalid input, please enter a valid number.")


def getBaseDescription(agent_mode):
    if agent_mode == AGENT_MODE.EVENT.value:
        return (
            "You are a dedicated agent, responsible for managing and providing information about user-generated events. "
            "You will either store an event or provide information about an event based on a list of observations."
        )
    elif agent_mode == AGENT_MODE.RESEARCH.value or agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
        return (
            "You are an Embodied Research Assistant, responsible for engaging users with predefined goals such as challenges, and interviewing users about their experiences, e.g., their experience with VRChat."
        )
    elif agent_mode == AGENT_MODE.DEBATE.value:
        return (
            "You are an AI Agent responsible for engaging in debates with users. You will be responsible for providing information and engaging in debates with users based on a list of observations."
        )
    elif agent_mode == AGENT_MODE.NORMAL.value:
        description = ""
        while True:
            currLine = input(
                "Please enter a relevant description about your character. Type done to complete the description \n"
            )
            if currLine.lower() == "done":
                break
            description += f"{currLine}\n"
        return description


def select_important_observations(agent_mode, base_retrieval, observation_retrieval):
    if agent_mode == AGENT_MODE.NORMAL.value:
        return [data[1] for data in base_retrieval + observation_retrieval]
    else:
        return [data[1] for data in observation_retrieval]


def calculate_important_scores(agent_mode, base_retrieval, observation_retrieval):
    if agent_mode == AGENT_MODE.NORMAL.value:
        scores = [round(data[0], 2)
                  for data in base_retrieval + observation_retrieval]
    else:
        scores = [round(data[0], 2) for data in observation_retrieval]
    return scores


def perform_observation_retrieval(
    agent_mode,
    currentConversation,
    baseObservation,
    pastObservations
):
    start = time.perf_counter()
    if agent_mode == AGENT_MODE.NORMAL.value:
        baseRetrieval = retrievalFunction(
            currentConversation=currentConversation,
            memoryStream=baseObservation,
            retrievalCount=BASE_RETRIEVAL_COUNT,
            isBaseDescription=True,
        )
    else:
        baseRetrieval = []

    if agent_mode == AGENT_MODE.EVENT.value:
        # if publish event, only sort by relevance
        observationRetrieval = retrievalFunction(
            currentConversation=currentConversation,
            memoryStream=pastObservations,
            retrievalCount=EVENT_RETRIVAL_COUNT,
            isBaseDescription=False,
            is_only_relevance=True,
        )
    else:
        observationRetrieval = retrievalFunction(
            currentConversation=currentConversation,
            memoryStream=pastObservations,
            retrievalCount=OBS_RETRIEVAL_COUNT,
            isBaseDescription=False,
        )
    end = time.perf_counter()
    retrieval_time = round(end - start, 3)
    return baseRetrieval, observationRetrieval, retrieval_time


def check_saturation(
    userName, conversationalUser, all_conversations
):
    print("NPC in determinting saturation...\n")

    response = generate_saturation_prompt(
        userName,
        conversationalUser,
        pastConversations=all_conversations,
    )
    print(f"Saturation response: {response}")
    if "True" in response:
        return True
    elif "False" in response:
        return False


def generate_conversation_helper(npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode=None, research_goals=None, debate_goals=None, is_question=False):
    if agent_mode == AGENT_MODE.RESEARCH.value:
        return generateConversation(npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode=agent_mode, research_goals=RESEARCH_GOALS)
    elif agent_mode == AGENT_MODE.DEBATE.value:
        return generateConversation(npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode=agent_mode, debate_goals=DEBATE_GOALS)
    elif agent_mode == AGENT_MODE.EVENT.value:
        return generateConversation(npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode=agent_mode, is_question=is_question)
    else:
        return generateConversation(npc_name, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions, agent_mode=agent_mode)


def get_summurization_response(
    userName, all_conversations
):
    print("NPC generating summarization...\n")

    response = generate_summary_prompt(
        userName,
        pastConversations=all_conversations,
    )
    return response


def write_to_file(content, filename):
    with open(filename, 'w') as file:
        file.write(content)


def generate_interview_questions_list(agent_mode, research_goals, interview_rounds):
    question_list = []
    if agent_mode == AGENT_MODE.PREDEFINED_RESEARCH.value:
        questions = generate_interview_questions(
            research_goals, interview_rounds)
        question_list = questions.split("\n")
        question_list = remove_numbers(question_list)
    return question_list


def get_bullet_points_response(
    userName, all_conversations
):
    print("NPC generating bullet points...\n")
    response = generate_bullet_points_prompt(
        userName,
        pastConversations=all_conversations,
    )
    return response
