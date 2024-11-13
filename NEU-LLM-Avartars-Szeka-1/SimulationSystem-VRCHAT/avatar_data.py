# Summary of the current changes as part of integraqtion effort:
# Updated expression map to better reflect guidance scenarios
# Modified action map for more appropriate onboarding interactions
# Maintained core avatar control structure

# integration effort
avatar_expression_map = {
    "Happy": 2,      # For positive interactions and successful recommendations
    "Tease": 5,      # For playful world suggestions
    "Wink": 4,       # For friendly tips
    "Confused": 3,   # For clarifying user requests
    "Sad": 6,        # For unavailable features/worlds
    "Excited": 1,    # Replaces "Angry" - better suited for world recommendations
}

avatar_action_map = {
    "Wave Hands": 1,  # For greetings
    "Point": 3,      # For directing attention to specific features
    "Cheer": 4,      # For celebrating discoveries
    "Dance": 5,      # For showing fun aspects
    "Welcome": 6,    # Replaces "Backflip" - more appropriate for guiding
    "Gesture": 7,    # Replaces "Sadness" - for general interactions
}

avatar_voice = "nova"  # Keep existing voice setting


# integration effort
EXPRESSION_USAGE = {
    "Happy": "Use when successfully helping users",
    "Excited": "Use when introducing new worlds/features",
    "Confused": "Use when clarifying user requests",
    "Tease": "Use for playful world suggestions",
    "Wink": "Use when giving tips/hints",
    "Sad": "Use when features/worlds unavailable"
}












# avatar_expression_map = {
#     "Happy": 2,
#     "Tease": 5,
#     "Wink": 4,
#     "Confused": 3,
#     "Sad": 6,
#     "Angry": 1,
# }
# avatar_action_map = {
#     "Wave Hands": 1,
#     "Clap": 2,
#     "Point": 3,
#     "Cheer": 4,
#     "Dance": 5,
#     "Backflip": 6,
#     "Sadness": 7,
# }
# avatar_voice = "nova"
