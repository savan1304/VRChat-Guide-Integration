# Summary of the current changes as part of integration effort:

# 1. File Status:
#   How: Commented out entire file
#   Why: Using SimulationSystem-VRCHAT/enums.py
# 
# 2. Integration Impact:
#   How: No changes needed
#   Why: Enums handled by VRChat implementation
# 
# 3. Dependencies:
#   How: Update imports in any referencing files
#   Why: Point to SimulationSystem-VRCHAT/enums.py


# from enum import Enum

# class AVATAR_DATA(Enum):
#     AVATAR_EXPRESSION_MAP = "Avatar Expressions Map"
#     AVATAR_ACTION_MAP = "Avatar Actions Map"
#     AVATAR_VOICE = "Avatar Voice"

# class CONVERSATION_MODE(Enum):
#     TEXT = 1
#     AUDIO = 2

# class AGENT_MODE(Enum):
#     NORMAL = 1
#     EVENT = 2
#     RESEARCH = 3
#     DEBATE = 4
#     PREDEFINED_RESEARCH = 5
#     AAC = 6