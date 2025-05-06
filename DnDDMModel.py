import json
import random
from pathlib import Path
from ollama import chat
from util.llm_utils import pretty_stringify_chat, run_console_chat, ollama_seed as seed, tool_tracker
import sys

# Import the various modules (Battlemap, DNDCaCModel, DNDCombat, DNDShopKeep)
from BattleMap import Battlemap
from DNDCaCModel import playerCharCreate, fetch_race_data, fetch_class_level_features, apply_racial_bonuses
from DNDCombat import get_monster_data
from DNDShopKeep import load_items, generate_shop_inventory

# Initialize battlemap
battlemap = Battlemap(width=20, height=20)

# Load D&D items from the shop inventory
items = load_items()
shop_inventory = generate_shop_inventory(items)

# LLM system variables
sign_your_name = 'Gas Lighters'
model = 'llama3.2'
llm_temperature = 1.0  # Dynamic temperature variable
options = {'temperature': llm_temperature, 'max_tokens': 100}
messages = [{
    'role': 'system',
    'content': (
        "You are a Dungeon Master running a D&D 5e campaign. Guide the player through character creation, "
        "combat encounters, inventory management, and storyline progression. Respond to player input, "
        "and dynamically update the battlemap, combat mechanics, and shop inventory. "
        "Use the tools for relevant tasks, like creating a battlemap, rolling for skill checks, and generating shop inventories."
    )
}]

# Define tools available to the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_battlemap",
            "description": "Generate a battlemap for combat encounter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_position": {"type": "string"},
                    "enemy_position": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "display_shop_inventory",
            "description": "Generate and display shop inventory for player to browse.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "roll_for",
            "description": "Roll a D20 to determine success or failure of a skill check.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "dc": {"type": "integer"},
                    "player": {"type": "string"}
                }
            }
        }
    }
]

# Function to initiate character creation using DNDCaCModel
def create_character():
    name = input("Enter character name: ")
    age = int(input("Enter age: "))
    level = int(input("Enter level: "))
    gender = input("Enter gender: ")
    description = input("Enter character description: ")
    background = input("Enter background: ")
    playerclass = input("Enter class (e.g., wizard, fighter): ").lower()
    race = input("Enter race (e.g., human, elf): ").lower()

    # Assign stats using standard array
    stats = {}
    abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
    available_stats = [15, 14, 13, 12, 10, 8]

    for ability in abilities:
        stat_value = int(input(f"Assign value to {ability}: "))
        stats[ability] = stat_value
        available_stats.remove(stat_value)

    # Apply racial bonuses (Human gives +1 to all stats)
    race_data = fetch_race_data(race)
    stats = apply_racial_bonuses(stats, race_data)

    # Create character
    character = playerCharCreate(
        name=name,
        age=age,
        level=level,
        gender=gender,
        description=description,
        background=background,
        playerclass=playerclass,
        race=race,
        stats=stats,
        class_features=[],
        race_features=[]
    )

    print(f"Character created: {character.name}, {character.race}, {character.playerclass}")

    # Save character to JSON file
    character_data = {
        'name': character.name,
        'age': character.age,
        'level': character.level,
        'gender': character.gender,
        'description': character.description,
        'background': character.background,
        'playerclass': character.playerclass,
        'race': character.race,
        'stats': character.stats,
        'class_features': character.class_features,
        'race_features': character.race_features
    }

    # Save to a JSON file
    save_path = Path(f"{character.name}_character.json")
    with open(save_path, 'w') as json_file:
        json.dump(character_data, json_file, indent=4)

    print(f"Character saved to {save_path}")
    return character

def process_function_call(function_call):
    name = function_call.name
    args = function_call.arguments
    return globals()[name](**args)

@tool_tracker
def roll_for(skill, dc, player):
    global llm_temperature
    roll = random.randint(1, 20)

    # Adjust temperature based on criticals
    if roll == 1:
        llm_temperature = min(llm_temperature + 1.0, 2.0)
        print("Critical failure! Increasing LLM temperature.")
    elif roll == 20:
        llm_temperature = max(llm_temperature - 1.0, 0.0)
        print("Critical success! Decreasing LLM temperature.")

    result = "Success" if roll >= dc else "Failure"
    return f"{player} rolled a {roll} for {skill} (DC {dc}): {result} (LLM Temp: {llm_temperature})"

@tool_tracker
def display_shop_inventory():
    return generate_shop_inventory(items)

@tool_tracker
def create_battlemap(player_position, enemy_position):
    return battlemap.generate_map(player_position, enemy_position)

@tool_tracker
def combat_encounter(character, monster_name):
    monster_data = get_monster_data(monster_name)
    if not monster_data:
        print(f"Could not find monster data for {monster_name}")
        return

    print(f"Combat starts! {character.name} faces a {monster_name}")

    while character.hit_points > 0 and monster_data['hit_points'] > 0:
        action = input("What action do you want to take? (e.g., Attack, Defend, Cast spell): ")

        if action.lower() == 'attack':
            damage = random.randint(1, 10)
            monster_data['hit_points'] -= damage
            print(f"You dealt {damage} damage to {monster_name}. Monster HP: {monster_data['hit_points']}")

            roll_chat = {
                'model': model,
                'temperature': llm_temperature,
                'messages': [{
                    "role": "system",
                    "content": f"{character.name} attacks the {monster_name}. Determine if they hit using a D20 roll."
                }],
                'tools': tools
            }

            response = run_console_chat(roll_chat)

            if response.message.tool_calls and response.message.tool_calls[0].function.name == "roll_for":
                result = process_function_call(response.message.tool_calls[0].function)
                print(result)
        else:
            print(f"{action} is not a valid action in combat.")
            break

        # Monster's attack
        monster_attack = random.randint(1, 10)
        character.hit_points -= monster_attack
        print(f"The {monster_name} attacks and deals {monster_attack} damage. Your HP: {character.hit_points}")

    if character.hit_points <= 0:
        print(f"{character.name} has been defeated!")
    else:
        print(f"You defeated the {monster_name}!")

def start_campaign():
    print("Welcome to the D&D Campaign! Let's create your character.")
    character = create_character()

    while True:
        print("What would you like to do?")
        action = input("Options: [1] Explore, [2] Combat, [3] Visit Shop, [4] Exit Campaign: ")

        if action == '1':
            print("You are exploring the world!")
        elif action == '2':
            print("Enter combat mode!")
            monster_name = input("Enter the name of the monster to fight: ")
            combat_encounter(character, monster_name)
        elif action == '3':
            print("Visiting the shop!")
            inventory = display_shop_inventory()
            print("The following items are available for purchase:")
            for item in inventory:
                print(f"{item['Name']} (ID: {item['ID']}) - {item['Cost_gp']} gold")
        elif action == '4':
            print("Exiting the campaign.")
            break
        else:
            print("Invalid option. Please choose again.")

# Start the campaign
start_campaign()
