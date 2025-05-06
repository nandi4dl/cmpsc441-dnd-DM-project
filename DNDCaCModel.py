import sys
from pathlib import Path
import requests
from dnd_character import *
import json

# Ollama setup
from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed

def playerCharCreate(name, age, level, gender, description, background, playerclass, race, stats, class_features, race_features):
    newChar = Character(
        name=name,
        age=age,
        level=level,
        gender=gender,
        description=description,
        background=background,
        classs=CLASSES[playerclass.lower()],
        race=race,
        stats=stats,
        class_features=class_features,
        race_features=race_features
    )
    return newChar

# Basic config
sign_your_name = 'Gas Lighters'
model = 'llama3.2'
options = {'temperature': 0.1, 'max_tokens': 100}

messages = [{
    'role': 'system',
    'content': (
        "You are a Dungeon Master helping a player create a D&D 5e character. "
        "Ask for character name, age, level, gender, description, background, class, race, and stats. "
        "Let the player assign stats using the standard array {15, 14, 13, 12, 10, 8} to the six abilities: "
        "Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma. "
        "After stats are assigned, apply any racial bonuses (fetched via API). "
        "Fetch class features for the provided level and race traits (also fetched via API). "
        "Be sure to fetch **Human racial bonuses** and apply +1 to all stats. "
        "Display the racial traits, class features, and background options accordingly. "
        "Provide starter items based on class and background, including gear and gold. "
        "Ensure the racial and class bonuses are properly applied before proceeding with character creation. "
        "Only show the background options that fit with the character's background (e.g., for Entertainer). "
        "Be warm, friendly, and immersive in your approach."
    )
}, {
    'role': 'assistant',
    'content': (
        "Welcome to the D&D Character Creator! Let's start by creating your character. "
        "I'll ask you for some details to build the perfect character for you."
    )
}]

options |= {'seed': seed(sign_your_name)}

def seed(name):
    return sum(ord(c) for c in name) % 100  

# Helper: Fetch race data
def fetch_race_data(race_index):
    base_url = 'https://www.dnd5eapi.co'
    resp = requests.get(f'{base_url}/api/2014/races/{race_index}')
    if resp.status_code == 200:
        return resp.json()
    return {}

# Helper: Apply racial bonuses
def apply_racial_bonuses(stats, race_data):
    if race_data['index'] == 'human':
        for ability in stats:
            stats[ability] += 1  
    else:
        for bonus in race_data.get('ability_bonuses', []):
            ability = bonus['ability_score']['name'].upper()
            if ability in stats:
                stats[ability] += bonus['bonus']
    return stats

def safe_input(prompt):
    user_input = input(prompt)
    if user_input.strip().lower() == '/exit':
        print("Exiting character creator.")
        sys.exit()
    return user_input

# Helper: Collect user input via Ollama
def get_user_input(prompt):
    messages.append({'role': 'user', 'content': prompt})
    response = chat(model=model, messages=messages, stream=False, options=options)
    messages.append({'role': 'assistant', 'content': response.message.content})
    return response.message.content

# Start interaction
print("Welcome to the D&D Character Creator! Type '/exit' to quit at any time.")

while True:
    user_input = safe_input("You: ")
    if user_input.strip().lower() == '/exit':
        break

    messages.append({'role': 'user', 'content': user_input})
    response = chat(model=model, messages=messages, stream=False, options=options)
    print(f'Agent: {response.message.content}')
    messages.append({'role': 'assistant', 'content': response.message.content})

# Get final character details
print("\n--- Let's finalize your character! ---")

# Ask details one-by-one
name = safe_input("Character Name: ")
age = safe_input("Age: ")
level = int(safe_input("Level: "))
gender = safe_input("Gender: ")
description = safe_input("Description: ")
background = safe_input("Background: ")
playerclass = safe_input("Class: ").lower()
race = safe_input("Race (e.g. human, elf, dwarf): ").lower()

# Standard array assignment
print("Assign these values to the 6 stats: 15, 14, 13, 12, 10, 8")
abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
assigned_stats = {}
used_values = []

for ability in abilities:
    while True:
        try:
            val = int(safe_input(f"Assign value to {ability}: "))
            if val in [15, 14, 13, 12, 10, 8] and val not in used_values:
                assigned_stats[ability.upper()] = val
                used_values.append(val)
                break
            else:
                print("Value already used or invalid. Try again.")
        except ValueError:
            print("Invalid number. Try again.")

# Apply race bonuses 
race_data = fetch_race_data(race)
if not race_data:
    print("Invalid race. No bonuses applied.")
else:
    assigned_stats = apply_racial_bonuses(assigned_stats, race_data)

# Fetch class level features 
def fetch_class_level_features(class_name, level):
    url = f"https://www.dnd5eapi.co/api/classes/{class_name.lower()}/levels/{level}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

# Fetch race-specific features 
def fetch_race_features(race_name):
    base_url = "https://www.dnd5eapi.co"
    race_url = f"{base_url}/api/races/{race_name}/traits"
    response = requests.get(race_url)
    if response.status_code == 200:
        return response.json()
    return {}

# Get class features for the selected class and level
class_level_features = fetch_class_level_features(playerclass, level)
if not class_level_features:
    print(f"Failed to fetch class features for level {level} {playerclass.capitalize()}.")
else:
    print(f"\nClass Features for Level {level} {playerclass.capitalize()}:")
    for feature in class_level_features.get('features', []):
        print(f"- {feature['name']}")

# Get race features for the selected race
race_features = fetch_race_features(race)

# Create the character
character = playerCharCreate(
    name=name,
    age=age,
    level=level,
    gender=gender,
    description=description,
    background=background,
    playerclass=playerclass,
    race=race,
    stats=assigned_stats,
    class_features=class_level_features.get('features', []),
    race_features=race_features.get('traits', [])
)

# Show final stats and class-specific features
print("\n--- Final Character Sheet ---")
print(character)

# Show stats with racial bonuses
print("\nStats with Racial Bonuses:")
for stat, val in assigned_stats.items():
    print(f"{stat}: {val}")

# Save chat log
with open(Path('./attempts.txt'), 'a') as f:
    f.write('-------------------------NEW ATTEMPT-------------------------\n\n\n')
    f.write(f'Model: {model}\nOptions: {options}\n')
    f.write(pretty_stringify_chat(messages))
    f.write('\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n')