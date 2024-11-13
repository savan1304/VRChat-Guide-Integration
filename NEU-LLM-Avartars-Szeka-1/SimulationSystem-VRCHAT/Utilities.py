# Summary of the current changes as part of integration effort:

# 1. Utility Functions:
#   How: Kept all functions unchanged
#   Why: Provides essential byte handling for VRChat data processing
# 
# 2. Integration Impact:
#   How: Functions remain available for use across codebase
#   Why: Supports general data handling needs
# 
# 3. Dependencies:
#   How: No changes needed
#   Why: Functions are generic and don't conflict with onboarding agent


def safe_decode(data):
    encodings = ['utf-8', 'utf-16', 'gbk', 'iso-8859-1', 'iso-8859-5', 'iso-8859-6', 'big5', 'shift_jis', 'euc-kr', 'euc-jp', 'windows-1252', 'windows-1251', 'windows-1256']
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode('utf-8', 'replace')  # Default to utf-8 with replacement


# Convert bytes to string recursively over a dictionary or list and decode bytes safely into a string
def handle_bytes(obj):
    if isinstance(obj, bytes):
        return safe_decode(obj)
    elif isinstance(obj, list):
        return [handle_bytes(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: handle_bytes(value) for key, value in obj.items()}
    else:
        return obj
