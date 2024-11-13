# Summary of the current changes as part of integration effort:
# 1. get_npc_name():
#   How: Simplified to always return "VRChatGuide"
#   Why: We only need one fixed agent type for VRChat guidance

# 2. getBaseDescription():
#   How: Updated description to focus on VRChat guidance
#   Why: Provides clear purpose for the onboarding agent

# 3. generate_conversation_helper():
#   How: Removed research/debate parameters, focused on basic conversation
#   Why: Streamlines conversation generation for world/event recommendations

# 4. is_question_function():
#   How: Kept core functionality, optimized keywords
#   Why: Essential for detecting user questions about VRChat features
# 
# 5. set_agent_mode():
#   How: Simplified to return only NORMAL mode
#   Why: Other modes (research, debate) aren't needed for VRChat guidance
# 
# 6. Commented Out Functions:
#   remove_numbers(): Not needed without interview functionality
#   perform_summurization_logic(): Not needed without language learning features


from enums import CONVERSATION_MODE, AGENT_MODE
import re
from responseGenerator import generate_saturation_prompt, generate_summary_prompt, generateConversation
from retrievalFunction import retrievalFunction
import time

BASE_RETRIEVAL_COUNT = 3  # change parameter
OBS_RETRIEVAL_COUNT = 5  # change parameter
RA_RETRIVAL_COUNT = 5
EVENT_RETRIVAL_COUNT = 5

# Not needed for VRChat onboarding agent - specific to research/debate modes
# RESEARCH_GOALS = "experience in Vr chat, what activities they like doing in Vr chat and overall why do they value regarding VR chat?"
# DEBATE_GOALS = "AI Agents should be included in VRChat in the future"
# INTERVIEW_ROUNDS = 3

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

def filter_conversation(conversation):
    # Remove text within parentheses
    filtered_result = re.sub(r'\([^()]*\)', '', conversation)
    # Remove newline characters
    filtered_result = filtered_result.replace('\n', '')
    return filtered_result

def write_to_file(content, filename):
    with open(filename, 'w') as file:
        file.write(content)


# integration effort
def get_npc_name(agent_mode):
    return "VRChatGuide"


# integration effort
def getBaseDescription(agent_mode):
    return "You are a VRChat guide helping users discover worlds and events, providing recommendations and assistance with VRChat features."


# integration effort
def generate_conversation_helper(npc_name, conversationalUser, currentConversation, important_observations,
                               avatar_expressions, avatar_actions):
    return generateConversation(npc_name, conversationalUser, currentConversation,
                              avatar_expressions, avatar_actions)

# integration effort
def is_question_function(message):
    # Useful for detecting questions about VRChat features/worlds
    question_keywords = ["what", "how", "where", "when", "why", "who", "?"]
    message_lower = message.lower()
    for keyword in question_keywords:
        if keyword in message_lower:
            return True
    return False


# integration effort
def set_agent_mode():
    # Simplify to only VRChat Guide mode
    return AGENT_MODE.NORMAL.value



# Not needed for VRChat onboarding agent - specific to interview functionality
# def remove_numbers(question_list):
#     processed_questions = []
#     for question in question_list:
#         # Find the index of the first non-digit character in the question
#         index = 0
#         for char in question:
#             if not char.isdigit():
#                 break
#             index += 1
#         # Remove the numbers and any leading whitespace
#         processed_question = question[index:].lstrip()
#         processed_questions.append(processed_question)
#     return processed_questions


# Not needed for VRChat onboarding agent - specific to language learning retrieval
# def select_important_observations(agent_mode, base_retrieval, observation_retrieval):
#     if agent_mode == AGENT_MODE.NORMAL.value:
#         return [data[1] for data in base_retrieval + observation_retrieval]
#     else:
#         return [data[1] for data in observation_retrieval]


# Not needed for VRChat onboarding agent - specific to language learning retrieval
# def calculate_important_scores(agent_mode, base_retrieval, observation_retrieval):
#     if agent_mode == AGENT_MODE.NORMAL.value:
#         scores = [round(data[0], 2) for data in base_retrieval + observation_retrieval]
#     else:
#         scores = [round(data[0], 2) for data in observation_retrieval]
#     return scores


# Not needed for VRChat onboarding agent - specific to language learning retrieval
# def perform_observation_retrieval(
#         agent_mode,
#         currentConversation,
#         baseObservation,
#         pastObservations
#     ):
#     start = time.perf_counter()
#     if agent_mode == AGENT_MODE.NORMAL.value:
#         baseRetrieval = retrievalFunction(
#             currentConversation=currentConversation,
#             memoryStream=baseObservation,
#             retrievalCount=BASE_RETRIEVAL_COUNT,
#             isBaseDescription=True,
#         )
#     else:
#         baseRetrieval = []

#     if agent_mode == AGENT_MODE.EVENT.value:
#         # if publish event, only sort by relevance
#         observationRetrieval = retrievalFunction(
#             currentConversation=currentConversation,
#             memoryStream=pastObservations,
#             retrievalCount=EVENT_RETRIVAL_COUNT,
#             isBaseDescription=False,
#             # is_only_relevance=True,
#         )
#     else:
#         observationRetrieval = retrievalFunction(
#             currentConversation=currentConversation,
#             memoryStream=pastObservations,
#             retrievalCount=OBS_RETRIEVAL_COUNT,
#             isBaseDescription=False,
#         )
#     end = time.perf_counter()
#     retrieval_time = round(end - start, 3)
#     return baseRetrieval, observationRetrieval, retrieval_time

# Not needed for VRChat onboarding agent - specific to language learning retrieval
# def perform_saturation_logic(
#         userName, conversationalUser, all_conversations
#     ):
#     print("NPC in determinting saturation...\n")

#     response = generate_saturation_prompt(
#         userName,
#         conversationalUser,
#         pastConversations=all_conversations,
#     )
#     print(f"Saturation response: {response}")
#     if "True" in response:
#         return True
#     elif "False" in response:
#         return False

# Not needed for VRChat onboarding agent - specific to language learning retrieval
# def perform_summurization_logic(
#         userName, all_conversations
#     ):
#     print("NPC generating summarization...\n")

#     response = generate_summary_prompt(
#         userName,
#         pastConversations=all_conversations,
#     )
#     return response




