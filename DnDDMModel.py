# big ol comment, the server stuff was added pretty late and couldn't spend enough time testing things
# might work with the right targets and the like, but I had no targets to test, so I can't tell

import json
import random
import sys
from pathlib import Path
from ollama import chat  
from llm_utils import pretty_stringify_chat, ollama_seed as seed, tool_tracker

# Import modules
from BattleMap import Battlemap
from DNDCaCModel import playerCharCreate, save_character_to_json, fetch_race_data, fetch_race_features, fetch_class_level_features, apply_racial_bonuses
from DNDCombat import get_monster_data
from DNDShopKeep import load_items, generate_shop_inventory
from base import Player, DungeonMaster

# Player setup
# player = Player("Dudley")
# player.connect()

# LLM config
sign_your_name = 'Gas Lighters'
model = 'llama3.2'
llm_temperature = 0
options = {'max_tokens': 100, 'seed': seed(sign_your_name)}  

# LLM system prompt 
messages = [{
    'role': 'system',
    'content': (
        "You are a Dungeon Master running a D&D 5e campaign. Guide the player through character creation, "
        "combat encounters, inventory management, and storyline progression. Respond to player input, "
        "and dynamically update the battlemap, combat mechanics, and shop inventory. "
        "You have the following tools available for use: \n\n"
        "1. /create_character - Initiates the character creation process.\n"
        "2. /shop - Displays the shop inventory for the player.\n"
        "3. /roll - Allows rolling for skills (e.g., Strength, Dexterity, etc.).\n"
        "4. /battlemap - Creates a battlemap with player and enemy positions.\n\n"
        "When appropriate, you can use the tools yourself or ask the Player themselves to do so"
        "Constantly refer to the Player's(s) character sheet(s) when necessary"
        "Respond to player input accordingly."
    )
}]

# DM setup (commenting out the server-related code)
# dm = DungeonMaster()
# dm.start_server()

# === Tool Function Definitions ===
def tool_tracker(func):
    """Modified to avoid unnecessary logging of tool calls."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper

@tool_tracker
def roll_for(skill, dc, player):
    global llm_temperature
    roll = random.randint(1, 20)
    if roll == 1:
        llm_temperature = min(llm_temperature + 1.0, 2.0)
    elif roll == 20:
        llm_temperature = max(llm_temperature - 1.0, 0.0)
    result = "Success" if roll >= dc else "Failure"
    return f"{player} rolled a {roll} for {skill} (DC {dc}): {result} (LLM Temp: {llm_temperature})"

@tool_tracker
def display_shop_inventory():
    items = load_items()  
    inventory = generate_shop_inventory(items)
    return "\n".join(
        f"- {item['Name']} (ID: {item['ID']}, Category: {item['Category']}, Cost: {item['Cost_gp']} gp, Weight: {item['Weight']})"
        for item in inventory
    )

@tool_tracker
def create_battlemap(player_position, enemy_position):
    battlemap = Battlemap(width=20, height=20)
    return battlemap.generate_map(player_position, enemy_position)

@tool_tracker
def create_character():
    print("Welcome to the D&D Character Creator! Type '/exit' to quit at any time.")
    name = input("Character Name: ")
    age = input("Age: ")
    level = int(input("Level: "))
    gender = input("Gender: ")
    description = input("Description: ")
    background = input("Background: ")
    playerclass = input("Class: ").lower()
    race = input("Race (e.g. human, elf, dwarf): ").lower()

    print("Assign these values to the 6 stats: 15, 14, 13, 12, 10, 8")
    abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
    assigned_stats = {}
    used_values = []

    for ability in abilities:
        while True:
            try:
                val = int(input(f"Assign value to {ability}: "))
                if val in [15, 14, 13, 12, 10, 8] and val not in used_values:
                    assigned_stats[ability.upper()] = val
                    used_values.append(val)
                    break
                else:
                    print("Value already used or invalid. Try again.")
            except ValueError:
                print("Invalid number. Try again.")

    # Fetch race data and apply racial bonuses
    race_data = fetch_race_data(race)
    if not race_data:
        print("Invalid race. No bonuses applied.")
    else:
        assigned_stats = apply_racial_bonuses(assigned_stats, race_data)

    # Fetch class features
    class_level_features = fetch_class_level_features(playerclass, level)
    if not class_level_features:
        print(f"Failed to fetch class features for level {level} {playerclass.capitalize()}.")
    else:
        print(f"\nClass Features for Level {level} {playerclass.capitalize()}:")
        for feature in class_level_features.values():
            print(f"- {feature['name']}")

    # Fetch race features
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
        class_features=class_level_features
    )

    print("\n--- Final Character Sheet ---")
    print(character)
    print("\nStats with Racial Bonuses:")
    for stat, val in assigned_stats.items():
        print(f"{stat}: {val}")
    
    # Save the character immediately after creation
    save_character_to_json({
        "name": character.name,
        "age": character.age,
        "level": character.level,
        "gender": character.gender,
        "description": character.description,
        "background": character.background,
        "class": character.classs,
        "class_features": character.class_features,
        "stats": assigned_stats,
        "race_traits": race_features.get('traits', [])
    })

    return f"Character created and saved: {character.name}"

def seed(name):
    return sum(ord(c) for c in name) % 100

def load_character_from_json(character_name):
    try:
        filename = f"{character_name.lower().replace(' ', '_')}.json"
        with open(filename, 'r') as file:
            character_data = json.load(file)
        print(f"Character {character_name} loaded successfully.")
        return character_data
    except FileNotFoundError:
        print(f"Character file {filename} not found.")
        return None
    except Exception as e:
        print(f"Error loading character data: {e}")
        return None

# === Run Console Chat ===

def safe_input(prompt):
    user_input = input(prompt)
    if user_input.strip().lower() == '/exit':
        print("Exiting game.")
        sys.exit()

    # Process tool calls
    if user_input.strip().lower() == '/create_character':
        print("Starting character creation process...")
        character = create_character()
        return f"Character created: {character}"

    elif user_input.strip().lower() == '/battlemap':
        print("Triggering create_battlemap tool...")
        player_position = input("Enter player position (x,y): ")
        enemy_position = input("Enter enemy position (x,y): ")
        battlemap = create_battlemap(player_position, enemy_position)
        return battlemap

    elif user_input.strip().lower() == '/shop':
        print("Displaying shop inventory...")
        inventory = display_shop_inventory()
        return inventory

    elif user_input.strip().lower() == '/roll':
        print("Triggering roll_for tool...")
        skill = input("Enter skill (e.g., Strength, Dexterity): ")
        dc = int(input("Enter DC value: "))
        player = input("Enter player name: ")
        result = roll_for(skill, dc, player)
        return result

    return user_input

def run_console_chat(chat_payload):
    """Send the conversation to the model and handle the response."""
    response = chat(
        model=chat_payload['model'],
        messages=chat_payload['messages']
    )
    return process_llm_response(response)

# === Process LLM Response ===

def process_llm_response(response):
    try:
        content = response['message']['content'].strip().lower()

        return content 

    except Exception as e:
        print(f"Error processing LLM response: {e}")
        return "There was an error processing your request."

# === Load character and attempts from .json and attempts.txt ===

def load_character(character_name):
    try:
        filename = f"{character_name.replace(' ', '_').lower()}.json"
        with open(filename, 'r') as file:
            character_data = json.load(file)
        return character_data
    except FileNotFoundError:
        print(f"Character file for {character_name} not found.")
        return None

def load_attempts_log():
    try:
        with open('./attempts.txt', 'r') as f:
            attempts = f.read().splitlines()
        return "\n".join(attempts[-5:])
    except FileNotFoundError:
        print("Attempts log not found.")
        return ""

    
# === Main Game Loop ===

print("Welcome to the DM Simulator! Type '/exit' to quit at any time.")
print("Available Commands (use when appropriate):")
print("/create_character - Start the character creation process.")
print("/battlemap - Create a battlemap with player and enemy positions.")
print("/shop - View the shop inventory and buy items.")
print("/roll - Roll for a skill check or attack roll.")
print("/load_character [character_name] - Load an existing character from a JSON file.")
print("/load_chat_history - View past chat interactions.")
print("/exit - Exit the game.")

while True:
    user_input = safe_input("You: ")

    if user_input.lower().startswith('/load_character'):
        character_name = user_input.split(" ", 1)[1].strip()
        character_data = load_character(character_name)
        if character_data:
            print(f"Loaded character data: {character_data}")
        continue

    if user_input.strip().lower() == '/load_chat_history':
        attempts_log = load_attempts_log()
        print(f"Attempts Log:\n{attempts_log}")
        continue

    # Prepare chat payload with messages
    messages.append({'role': 'user', 'content': user_input})

    # Prepare chat payload with messages
    chat_payload = {
        "model": model,
        "messages": messages
    }

    # Call LLM and get a response
    response = run_console_chat(chat_payload)

    if 'message' in response:
        print(f"\nDM: {response['message']['content']}\n")
        messages.append({'role': 'assistant', 'content': response['message']['content']})

    chat_log_path = Path('./attempts.txt')

    # Save the chat log after every interaction
    with open(chat_log_path, 'a') as f:
        f.write('-------------------------NEW ATTEMPT-------------------------\n\n\n')
        f.write(f'Model: {model}\nOptions: {options}\n')
        f.write(pretty_stringify_chat(messages))
        f.write('\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n')
