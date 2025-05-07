import sys
import json
from pathlib import Path
import requests

# Assuming the Character class and other helpers are defined as they were in the previous code.
from dnd_character import *

def playerCharCreate(name, age, level, gender, description, background, playerclass, class_features):
    newChar = Character(
        name=name,
        age=age,
        level=level,
        gender=gender,
        description=description,
        background=background,
        classs=CLASSES[playerclass.lower()],
        class_features=class_features
    )
    return newChar

def save_character_to_json(character_data):
    try:
        # Ensure that classs and other non-serializable attributes are handled properly
        def convert_non_serializable(obj):
            """Helper function to convert non-serializable objects to serializable forms."""
            # If the object is a dictionary, we iterate through the items
            if isinstance(obj, dict):
                return {key: convert_non_serializable(value) for key, value in obj.items()}
            # If the object is a list, we iterate through the list
            elif isinstance(obj, list):
                return [convert_non_serializable(item) for item in obj]
            # If the object is a custom class, handle it differently
            elif hasattr(obj, '__dict__'):
                # Convert an object with __dict__ (typically an instance of a class) to a dictionary
                return {key: convert_non_serializable(value) for key, value in vars(obj).items()}
            # If it's a string, don't do anything since it's already serializable
            elif isinstance(obj, str):
                return obj
            # If it's a non-string object, we can attempt to convert to string
            return str(obj)

        # Convert the character data to be fully serializable
        serializable_data = convert_non_serializable(character_data)

        # Use the character's name as the filename
        filename = f"{serializable_data['name'].replace(' ', '_').lower()}.json"

        # Save the character data to the file
        with open(filename, 'w') as file:
            json.dump(serializable_data, file, indent=4)

        print(f"Character data saved to {filename}")
    except Exception as e:
        print(f"Error saving character data: {e}")

# Helper: Fetch race data
def fetch_race_data(race_index):
    base_url = 'https://www.dnd5eapi.co'
    resp = requests.get(f'{base_url}/api/races/{race_index}')
    if resp.status_code == 200:
        return resp.json()
    return {}

# Helper: Apply racial bonuses
def apply_racial_bonuses(stats, race_data):
    if race_data.get('index') == 'human':
        for ability in stats:
            stats[ability] += 1
    else:
        for bonus in race_data.get('ability_bonuses', []):
            ability = bonus['ability_score']['name'].upper()
            if ability in stats:
                stats[ability] += bonus['bonus']
    return stats

# Helper: Fetch class level features (adjusted for the correct structure)
def fetch_class_level_features(class_name, level):
    url = f"https://www.dnd5eapi.co/api/classes/{class_name.lower()}/levels/{level}"
    response = requests.get(url)
    if response.status_code == 200:
        features_data = response.json()
        class_features = {}
        for feature in features_data.get('features', []):
            class_features[feature['index']] = feature
        return class_features
    return {}

# Helper: Fetch race features
def fetch_race_features(race_name):
    base_url = "https://www.dnd5eapi.co"
    race_url = f"{base_url}/api/races/{race_name}/traits"
    response = requests.get(race_url)
    if response.status_code == 200:
        return response.json()
    return {}

def safe_input(prompt):
    user_input = input(prompt)
    if user_input.strip().lower() == '/exit':
        print("Exiting character creator.")
        sys.exit()
    return user_input

def run_character_creation():
    # Start character creation
    print("Welcome to the DM Simulator! Type '/exit' to quit at any time.")

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

    # Apply racial bonuses
    race_data = fetch_race_data(race)
    if not race_data:
        print("Invalid race. No bonuses applied.")
    else:
        assigned_stats = apply_racial_bonuses(assigned_stats, race_data)

    # Get class features for the selected class and level
    class_level_features = fetch_class_level_features(playerclass, level)
    if not class_level_features:
        print(f"Failed to fetch class features for level {level} {playerclass.capitalize()}.")
    else:
        print(f"\nClass Features for Level {level} {playerclass.capitalize()}:")
        for feature in class_level_features.values():
            print(f"- {feature['name']}")

    # Get race features for the selected race
    race_features = fetch_race_features(race)

    # Create the character with class features passed as a dictionary
    character = playerCharCreate(
        name=name,
        age=age,
        level=level,
        gender=gender,
        description=description,
        background=background,
        playerclass=playerclass,
        class_features=class_level_features
    )

    character_data = {
        "name": name,
        "age": age,
        "level": level,
        "gender": gender,
        "description": description,
        "background": background,
        "class": playerclass,
        "class_features": class_level_features,
        "stats": assigned_stats,
        "race_traits": race_features.get('traits', [])
    }

    # Show final stats and class-specific features
    print("\n--- Final Character Sheet ---")
    print(character)

    # Show stats with racial bonuses
    print("\nStats with Racial Bonuses:")
    for stat, val in assigned_stats.items():
        print(f"{stat}: {val}")

    # Save character data to JSON file
    save_character_to_json(character_data)

if __name__ == "__main__":
    run_character_creation()
