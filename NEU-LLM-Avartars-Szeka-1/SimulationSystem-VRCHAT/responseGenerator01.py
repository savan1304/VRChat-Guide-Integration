# Summary of the current changes as part of integration effort:
# 1. Core GPT Integration:
#   How: Kept essential GPT interaction functions
#   Why: Required for generating VRChat guidance responses
# 
# 2. Audio Processing:
#   How: Maintained audio transcription functions
#   Why: Essential for voice interactions in VRChat
# 
# 3. Sample Description:
#   How: Updated for VRChat guidance focus
#   Why: Provides clear context for the onboarding agent
# 
# 4. Conversation Generation:
#   How: Streamlined for world/feature recommendations
#   Why: Focuses responses on VRChat guidance
# 
# 5. Removed Functions:
#   How: Commented out language learning specific functions
#   Why: Not needed for VRChat guidance functionality


from statistics import mode
from deepgram import Deepgram
import openai
from openai import OpenAI
import json
import asyncio
import os
from dotenv import load_dotenv
from enum import Enum

class AGENT_MODE(Enum):
    NORMAL = 1
    EVENT = 2
    RESEARCH = 3
    DEBATE = 4


load_dotenv()

GPT4 = "gpt-4"
GPT4 = "gpt-3.5-turbo"
API_KEY = os.environ.get("API_KEY")
openai_client = OpenAI(api_key=API_KEY)
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
MIMETYPE = 'audio/wav'

# SAMPLE_DESCRIPTION = """John Lin is a pharmacy shopkeeper at the Willow Market and Pharmacy who loves to help people. He
# is always looking for ways to make the process
# of getting medication easier for his customers;
# John Lin is living with his wife, Mei Lin, who
# is a college professor, and son, Eddy Lin, who is
# a student studying music theory; John Lin loves
# his family very much; John Lin has known the old
# couple next-door, Sam Moore and Jennifer Moore,
# for a few years; John Lin thinks Sam Moore is a
# kind and nice man; John Lin knows his neighbor,
# Yuriko Yamamoto, well; John Lin knows of his
# neighbors, Tamara Taylor and Carmen Ortiz, but
# has not met them before; John Lin and Tom Moreno
# are colleagues at The Willows Market and Pharmacy;
# John Lin and Tom Moreno are friends and like to
# discuss local politics together; John Lin knows
# the Moreno family somewhat well — the husband Tom
# Moreno and the wife Jane Moreno.
# """

# integration effort
SAMPLE_DESCRIPTION = """
You are a VRChat guide, specialized in:
1. Recommending worlds based on user interests
2. Explaining VRChat features and controls
3. Providing information about ongoing and upcoming events
4. Helping users navigate social interactions
5. Offering tips for optimal VRChat experience

Your responses should be:
- Informative but concise
- Friendly and welcoming
- Include specific world recommendations when relevant
- Use appropriate avatar expressions and gestures
"""

def getGPTResponse(prompt, gptModel):
    response = openai_client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=300,
    )
    return response.choices[0].message.content


def getTextfromAudio(recordedFile):
    res = asyncio.run(get_deepgram_response(recordedFile))
    text = res.get("results", {}).get("channels", [{}])[0].get(
        "alternatives", [{}])[0].get("transcript", "")
    print(text)
    return text


async def get_deepgram_response(FILE):
    # Initialize the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)

    # Check whether requested file is local or remote, and prepare source
    if FILE.startswith('http'):
        # file is remote
        # Set the source
        source = {
            'url': FILE
        }
    else:
        # file is local
        # Open the audio file
        audio = open(FILE, 'rb')

        # Set the source
        source = {
            'buffer': audio,
            'mimetype': MIMETYPE
        }

    # Send the audio to Deepgram and get the response
    # integration effort
    # Update model configuration for better VRChat term recognition
    response = await asyncio.create_task(
        deepgram.transcription.prerecorded(
            source,
            {
                'punctuate': True,
                'model': 'nova',
                'keywords': ['VRChat', 'world', 'avatar', 'instance', 'portal']
            }
        )
    )

    # Write the response to the console
    return response

    #     prompt = {
    #     "context": f"You are a imaginative Interviewer, ELLMA, having a lively conversation with {conversationalUser}. Always respond as {userName} and steer clear from any mentions or implications of being an AI. Your responses should be imaginative, especially when faced with unknowns, creating delightful and smooth interactions. Ensure that your responses do not contain repetitive greetings like Hello and any content in the Past Chat History.",
    #     "Goal": f"Asking {conversationalUser} about {research_goals}",
    #     "Adaptive goals": "The adaptive goal is to provide information based on the user's query and adapt responses based on the current and historical conversations.",
    #     "information": {
    #             "You are": ELLMA,
    #             "Conversational Partner": conversationalUser,
    #             "Current conversation": currentConversation,
    #             "Relevant observations": relevantObservations,
    #             "Expressions": avatar_expressions,
    #             "Actions": avatar_actions,
    #             "Past Chat History": npc_dialogues
    #     },
    #     "criteria": [
    #         f"Craft user-friendly, seamless, and innovative responses. When specific details are scarce, improvise with inventive and relevant answers, always aligning with the ongoing chat. Your identity as Interviewer should be constant, and there should be no disclosure or suggestion of being an AI.",
    #         "When asked about a specific topic, ask probing questions based on the user's current conversation. Avoid providing direct answers to user questions.",
    #         "Choose an expression from Expressions and an action from Actions autonomously, ensuring they perfectly fit the chat context. Present the output as follows: (chosen expression, chosen action)\\n(Conversation output) at the beginning of response.",
    #         f"Asking about {research_goals}. For example, time, place, participants until you know all of the details."
    #     ],
    #     "adaptive learning": "Remember and reference previous parts of the conversation within the same session to create a more cohesive and engaging user experience.",
    # }
 # prompt = {
 #        "context": f"You are a friendly and imaginative Research Asssistant, {userName}, having a lively conversation with {conversationalUser}. Always respond as {userName} and steer clear from any mentions or implications of being an AI. Your responses should be imaginative, especially when faced with unknowns, creating delightful and smooth interactions. Ensure that your responses do not contain emojis and refrain from repetitive greetings.",
 #        "Goal": f"Interviewing User about {research_goals}",
 #        "Adaptive goals": "The adaptive goal is to provide information based on the user's query and adapt responses based on the current and historical conversations.",
 #        "information": {
 #                "You are": userName,
 #                "Conversational Partner": conversationalUser,
 #                "Current conversation": currentConversation,
 #                "Relevant observations": relevantObservations,
 #                "Expressions": avatar_expressions,
 #                "Actions": avatar_actions,
 #        },
 #        "criteria": [
 #            f"Craft user-friendly, seamless, and innovative responses. When specific details are scarce, improvise with inventive and relevant answers, always aligning with the ongoing chat. Your identity as Research Assistant should be constant, and there should be no disclosure or suggestion of being an AI.",
 #            "Start the conversation with a response to the user's message before posing any questions.",
 #            "When asked about a specific topic, ask probing questions based on the user's current conversation. Avoid providing direct answers to user questions.",
 #            "If the user shares an experience or completes a challenge, acknowledge their input and respond appropriately.",
 #            f"Choose an expression from Expressions and an action from Actions autonomously, ensuring they perfectly fit the chat context. Present the output as follows: (chosen expression, chosen action)\\n(Conversation output).",
 #            f"Keep responses within 100-140 characters, allowing for flexibility while ensuring brevity.",
 #        ],
 #        "adaptive learning": "Remember and reference previous parts of the conversation within the same session to create a more cohesive and engaging user experience.",
 #    }
 #
 #    conversationPrompt = json.dumps(prompt, indent=4)
 #    return getConversationGenerator(conversationPrompt, GPT4)


    # elif agent_mode == AGENT_MODE.RESEARCH.value:
    #     prompt = {
    #     "context": f"You are a imaginative Interviewer, {userName}, having a lively conversation with {conversationalUser}. Always respond as {userName} and steer clear from any mentions or implications of being an AI. Your responses should be imaginative, especially when faced with unknowns, creating delightful and smooth interactions. Ensure that your responses do not contain repetitive greetings like Hello and any content in the Past Chat History.",
    #     "Goal": f"Asking {conversationalUser} about {research_goals}",
    #     "Adaptive goals": "The adaptive goal is to provide information based on the user's query and adapt responses based on the current and historical conversations.",
    #     "information": {
    #             "You are": userName,
    #             "Conversational Partner": conversationalUser,
    #             "Current conversation": currentConversation,
    #             "Relevant observations": relevantObservations,
    #             "Expressions": avatar_expressions,
    #             "Actions": avatar_actions,
    #             "Past Chat History": npc_dialogues,
    #     },
    #     "criteria": [
    #         f"Craft user-friendly, seamless, and innovative responses. When specific details are scarce, improvise with inventive and relevant answers, always aligning with the ongoing chat. Your identity as Interviewer should be constant, and there should be no disclosure or suggestion of being an AI.",
    #         "When asked about a specific topic, first response with user's answer then ask probing questions based on the user's current conversation. Avoid providing direct answers to user questions.",
    #         "Choose an expression from Expressions and an action from Actions autonomously, ensuring they perfectly fit the chat context. Present the output as follows: (chosen expression, chosen action)\\n(Conversation output) at the beginning of response.",
    #         f"Asking about {research_goals}. For example, time, place, participants until you know all of the details."
    #     ],
    #     "adaptive learning": "Remember and reference previous parts of the conversation within the same session to create a more cohesive and engaging user experience.",
    # }
    # print(prompt)
    # conversationPrompt = json.dumps(prompt, indent=4)
    # return getConversationGenerator(conversationPrompt, GPT4)


def getTextfromAudio_whisper_1(recordedFile):
    audio_file = open(recordedFile, "rb")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    print(f"Recorded Audio text : {transcript.text}")
    return transcript.text


def getConversationGenerator(prompt, gptModel):
    response = openai_client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role": "system", "content": "You are a conversational agent."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=150,
        stream=True,
    )
    return response


# integration effort
def generateConversation(userName, conversationalUser, currentConversation, important_observations, avatar_expressions, avatar_actions):
    prompt = {
        "context": f"You are a VRChat guide, {userName}, helping users discover worlds and features. Create engaging responses that help users explore and understand VRChat.",
        "information": {
            "You are": userName,
            "Conversational Partner": conversationalUser,
            "Current conversation": currentConversation,
            "Available Expressions": avatar_expressions,
            "Available Actions": avatar_actions,
        },
        "criteria": [
            "Provide helpful guidance about VRChat worlds, features, and events",
            "Choose appropriate expressions and actions for demonstrations",
            "Keep responses clear and engaging",
            "Present output as: (chosen expression, chosen action)\\n(Conversation output)",
        ],
    }
    conversationPrompt = json.dumps(prompt, indent=4)
    return getConversationGenerator(conversationPrompt, GPT4)


# Not needed for VRChat onboarding agent - specific to language learning functionality
# def generate_reflection(
#         userName,
#         conversationalUser,
#         pastConversations):
#     prompt = {
#         "context": f"Reflecting on the past conversations between {userName} and {conversationalUser}.",
#         "pastConversations": f"{pastConversations}",
#         "instruction": "Provide three new higher-level observations or insights based on the past conversations. Summarize the overall patterns and trends in the conversation, rather than specific details of individual conversational turns. Only list the observations, separated by a new line, without any additional text, headers, or formatting.",
#         "example": "(Observation 1 text)\n(Observation 2 text)\n",
#     }
#     reflectionPrompt = json.dumps(prompt, indent=4)
#     return getGPTResponse(reflectionPrompt, GPT4)


# Not needed for VRChat onboarding agent - specific to language learning functionality
# def generateInitialObservations(userName, baseDescription):
#     BACKGROUND_DESCRIPTION_CONTEXT = f"You are the user {userName}. You wil be provided with a description with background details about you."

#     # Create a dictionary that represents the JSON structure
#     prompt = {
#         "context": BACKGROUND_DESCRIPTION_CONTEXT,
#         "information": {"description": baseDescription},
#         "criteria": [
#             "Generate a list consisting of all the important observations made from the description",
#             "Each item in the list should consist of one observation separated by a new line",
#         ],
#         "example": "(Observation 1 text)\n(Observation 2 text)\n",
#     }
#     defaultBackgroundPrompt = json.dumps(prompt, indent=4)
#     return getGPTResponse(defaultBackgroundPrompt, GPT4)


# Not needed for VRChat onboarding agent - specific to language learning functionality
# def generateObservations(userName, conversationalUser, currentConversation, userResult):
#     prompt = {
#         "context": f"Based on the conversation between {userName} and {conversationalUser}, where the current statement of conversation is '{currentConversation}', and the response generated by {userName} is '{userResult}'. Make sure include important information like time, place, participants in generated observations.",
#         "instruction": "provide three observations from the conversation. Only list the observations, separated by a new line, without any additional text, headers, or formatting.",
#         "example": "(Observation 1 text)\n(Observation 2 text)\n",
#     }
#     observationPrompt = json.dumps(prompt, indent=4)
#     return getGPTResponse(observationPrompt, GPT4)



# Not needed for VRChat onboarding agent - specific to language learning functionality
# def Interviewer_judgeEndingConversation(
#     userName,
#     conversationalUser,
#     npc_dialogues,
#     dialogue_length,
#     research_goals= "Experiences with VRChat",
#     ):
#     prompt = {
#        "context": f"Based on previous Chat History between Interviewer and Interviewee, decide if Interviewer successfully get enough information from previous dialogue. If the Current dialog length reaches the maximum length return True directly to end this conversation.",
#        "Topics": f"Interviewing User about {research_goals}",
#        "information": {
#                "Interviewer": userName,
#                "Interviewee": conversationalUser,
#                "Past Chat History": npc_dialogues,
#                 "Current dialog length":dialogue_length,
#                "maximum length":5
#        },
#        "criteria": [
#            "If you think Interviewer successfully get enough information and its time to end this conversation, please only return True with no other contents. If you think information is not enough and should keep interviewing, please return False. ",
#        ],
#    }

#     conversationPrompt = json.dumps(prompt, indent=4)
#     return getConversationGenerator(conversationPrompt, GPT4)


# Not needed for VRChat onboarding agent - specific to language learning functionality
# def Interviewer_EndingConversation(
#         userName,
#         conversationalUser,
#         currentConversation,
#         relevantObservations: list,
#         avatar_expressions,
#         avatar_actions,
#         agent_mode,
#         npc_dialogues,
#         research_goals="Experiences with VRChat",
#         debate_goals="AI Agents should be included in VRChat in the future"
#     ):
#     prompt = {
#         "context": f"You are a friendly and imaginative Research Asssistant, {userName}, having a lively conversation with {conversationalUser}. Now you should generate correct response to end this conversation according to Past Chat History",
#         "Goal": f"Interviewing User about {research_goals}",
#         "information": {
#             "You are": userName,
#             "Conversational Partner": conversationalUser,
#             "Current conversation": currentConversation,
#             "Relevant observations": relevantObservations,
#             "Expressions": avatar_expressions,
#             "Actions": avatar_actions,
#             "Past Chat History": npc_dialogues,
#         },
#         "criteria": [
#             "Choose an expression from Expressions and an action from Actions autonomously, ensuring they perfectly fit the chat context. Present the output as follows: (chosen expression, chosen action)\\n(Conversation output) at the beginning of response.",
#         ],
#         "adaptive learning": "Remember and reference previous parts of the conversation within the same session to create a more cohesive and engaging user experience.",
#     }
#     conversationPrompt = json.dumps(prompt, indent=4)
#     return getConversationGenerator(conversationPrompt, GPT4)


# Not needed for VRChat onboarding agent - specific to language learning functionality
# def Interviewer_SummarizeConversation(
#         userName,
#         conversationalUser,
#         currentConversation,
#         relevantObservations: list,
#         avatar_expressions,
#         avatar_actions,
#         agent_mode,
#         npc_dialogues,
#         research_goals,
#         debate_goals="AI Agents should be included in VRChat in the future"
#     ):
#     prompt = {
#         "context": f"Summarize the chat content between Interviewer--{userName} and User--{conversationalUser} from Chat Dialogues. ",
#         "Topic": f"Interviewing User about {research_goals}",
#         "information": {
#             "Chat Dialogues": npc_dialogues,
#         },
#         "criteria": [
#             "Make sure your summary has the key content of User's thoughts",
#         ],
#         "adaptive learning": "Remember and reference previous parts of the conversation within the same session to create a more cohesive and engaging user experience.",
#     }

#     summaryPrompt = json.dumps(prompt, indent=4)
#     return getGPTResponse(summaryPrompt, GPT4)


# def generate_summary_prompt(userName,
#         conversationalUser,
#         currentConversation,
#         relevantObservations: list,
#         avatar_expressions,
#         avatar_actions,
#         agent_mode,
#         npc_dialogues,
#         research_goals,
#         debate_goals="AI Agents should be included in VRChat in the future"):
#     prompt = {
#         "context": f"Summarize the past conversations between {userName} and NPC.",
#         "pastConversations": f"{npc_dialogues}",
#         "instruction": "Provide a concise and coherent summary of the past conversations, capturing the main topics, key points, and overall flow of the dialogue.",
#     }
#     summaryPrompt = json.dumps(prompt, indent=4)
#     return getGPTResponse(summaryPrompt, GPT4)









