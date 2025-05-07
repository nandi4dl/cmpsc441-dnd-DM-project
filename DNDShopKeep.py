import random
import json
from pathlib import Path
import sys

# Load D&D items from the JSON file
def load_items(file_path='ItemList.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['items']

# Randomly select items for the shopkeeper's inventory
def generate_shop_inventory(items, num_items=5):
    return random.sample(items, num_items)

def run_shop():
    # Set up shopkeeper's inventory
    items = load_items()
    shop_inventory = generate_shop_inventory(items)

    # Display the inventory
    print("Welcome, adventurer! Here's what I have for sale today:")
    for item in shop_inventory:
        print(f"- {item['Name']} (ID: {item['ID']}, Category: {item['Category']}, Cost: {item['Cost_gp']} gp, Weight: {item['Weight']})")

    # Command-line interaction loop
    print("\nType the ID of an item to inspect it or type '/exit' to leave the shop.")
    while True:
        user_input = input("You: ").strip().lower()
        if user_input == '/exit':
            print("Farewell, traveler!")
            break

        # Look up item by ID
        found_item = next((item for item in shop_inventory if item['ID'] == user_input.zfill(3)), None)
        if found_item:
            print(f"\n{found_item['Name']} (ID: {found_item['ID']})")
            print(f"Category: {found_item['Category']}")
            print(f"Cost: {found_item['Cost_gp']} gp")
            print(f"Weight: {found_item['Weight']}")
        else:
            print("That item isn't in my shop today. Try another ID.")

# Use this when you want to run the shop
if __name__ == "__main__":
    run_shop()
