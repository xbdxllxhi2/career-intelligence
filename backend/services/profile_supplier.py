import  json
import os

PROFILE_FILE = "./input/context/profile.json"

def get_profile():
    if not os.path.exists(PROFILE_FILE):
     raise FileNotFoundError(f"{PROFILE_FILE} does not exist.")
    
    with open(PROFILE_FILE) as f:
        profile = json.load(f)
    return profile