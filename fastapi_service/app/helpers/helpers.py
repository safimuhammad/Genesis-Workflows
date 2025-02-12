import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json

def import_abilities():
    with open("../prompts/prompt_schema/abilities.json", "r") as f:
        abilities = json.load(f)["abilities"]

    return abilities
