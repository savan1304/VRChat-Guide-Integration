# Summary of the current changes as part of integration effort:

# AVATAR_DATA Enum:
#   How: Kept unchanged
#   Why: Essential for avatar control in VRChat

# CONVERSATION_MODE Enum:
#   How: Kept unchanged
#   Why: Needed for handling both text and audio interactions
# 
# AGENT_MODE Enum:
#   How: Simplified to only NORMAL mode
#   Why: Other modes were specific to language learning scenarios


from enum import Enum

class AVATAR_DATA(Enum):
    AVATAR_EXPRESSION_MAP = "Avatar Expressions Map"
    AVATAR_ACTION_MAP = "Avatar Actions Map"
    AVATAR_VOICE = "Avatar Voice"

class CONVERSATION_MODE(Enum):
    TEXT = 1
    AUDIO = 2

class AGENT_MODE(Enum):
    NORMAL = 1  # VRChat Guide mode


    # Not needed for VRChat onboarding agent - specific to language learning modes
    # EVENT = 2
    # RESEARCH = 3
    # DEBATE = 4
    # PREDEFINED_RESEARCH = 5