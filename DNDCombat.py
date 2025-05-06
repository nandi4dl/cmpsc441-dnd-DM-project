import requests
import re

# Tool function to get monster data from the D&D 5e API
def get_monster_data(monster_name):
    # Format monster name to match API endpoint
    formatted_monster_name = monster_name.replace(' ', '-').lower()
    url = f"https://www.dnd5eapi.co/api/monsters/{formatted_monster_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Parse the JSON response
    else:
        print(f"Error: Unable to fetch data for {monster_name}")
        return None

# Tool function to convert plural monster names to singular
def convert_plural_to_singular(name):
    # Simple rule to convert plural names to singular
    if name.endswith('s') and len(name) > 1:
        return name[:-1]  # Remove the last 's' for basic plural-to-singular
    return name

# Tool function to extract monster names from a given paragraph
def extract_monster_names(paragraph):
    # Match sequences of capitalized words
    possible_monster_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', paragraph)
    
    # Define common words that should not be considered part of the monster name
    common_words = {"the", "a", "an", "in", "on", "of", "and", "to", "at", "with", "later"}

    # Filter out common words 
    possible_monster_names = [name for name in possible_monster_names if name.lower() not in common_words]

    # Convert plural names to singular
    possible_monster_names = [convert_plural_to_singular(name) for name in possible_monster_names]

    return possible_monster_names

# Tool function to calculate CR from the monster's hit points and damage per round
def calculate_cr_from_monster(monster_data):
    # Simplified CR calculation based on HP and damage
    hp = monster_data['hit_points']
    damage_per_round = sum(get_average_damage(action) for action in monster_data['actions'])
    
    defensive_cr = hp / 10
    offensive_cr = damage_per_round / 5
    
    return (defensive_cr + offensive_cr) / 2

# Tool function to extract average damage from an action description
def get_average_damage(action):
    # Simplified damage calculation by extracting the damage formula
    match = re.search(r"(\d+d\d+)", action['desc'])
    if match:
        damage = match.group(1)
        dice_count, dice_type = map(int, damage.split('d'))
        avg_dice = (dice_count * (dice_type + 1)) / 2
        return avg_dice
    return 0

# Tool function to adjust monster's stats to match the target CR
def adjust_for_target_cr(monster_data, target_cr):
    current_cr = calculate_cr_from_monster(monster_data)
    
    if target_cr > current_cr:
        scale_factor = target_cr / current_cr
        monster_data['hit_points'] = int(monster_data['hit_points'] * scale_factor)
        for action in monster_data['actions']:
            action['desc'] = adjust_action_damage(action['desc'], scale_factor)
    
    elif target_cr < current_cr:
        scale_factor = current_cr / target_cr
        monster_data['hit_points'] = int(monster_data['hit_points'] / scale_factor)
        for action in monster_data['actions']:
            action['desc'] = adjust_action_damage(action['desc'], 1 / scale_factor)

# Tool function to adjust the damage in an action description based on scale factor
def adjust_action_damage(action_desc, scale_factor):
    match = re.search(r"(\d+d\d+)", action_desc)
    if match:
        damage = match.group(1)
        dice_count, dice_type = map(int, damage.split('d'))
        # Avoid "0dX" by ensuring at least 1 die is used
        new_dice_count = max(1, int(dice_count * scale_factor))  
        return action_desc.replace(damage, f"{new_dice_count}d{dice_type}")
    return action_desc
