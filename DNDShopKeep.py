import random
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[1]))

from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed

# Load D&D items from the JSON file
def load_items(file_path='ItemList.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['items']

# Randomly select items for the shopkeeper's inventory
def generate_shop_inventory(items, num_items=5):
    return random.sample(items, num_items)

# Set up shopkeeper's inventory
items = load_items()  # Load items from the ItemList.json
shop_inventory = generate_shop_inventory(items)  # Randomly select items

# Print the inventory for debugging
print("Shopkeeper's Inventory:")
for item in shop_inventory:
    print(f"- {item['Name']} (ID: {item['ID']})")

# Shopkeeper's role and system message for the LLM
sign_your_name = 'Gas Lighters'
model = 'llama3.2'
options = {'temperature': 0.1, 'max_tokens': 100}
messages = [{'role': 'system', 'content': 'You are a friendly and knowledgeable shopkeeper in a D&D campaign. You have an inventory of items for sale. The player can ask about your inventory and purchase items. Your responses should feel like a merchant talking to the player.'}]

# Include the inventory in the system message
inventory_description = "\n".join([f"{item['Name']} (ID: {item['ID']})" for item in shop_inventory])
messages.append({'role': 'system', 'content': f"Shopkeeper's Inventory: {inventory_description}"})

options |= {'seed': seed(sign_your_name)}

# Chat loop
while True:
    message = {'role': 'user', 'content': input('You: ')}
    messages.append(message)
    response = chat(model=model, messages=messages, stream=False, options=options)
    print(f'Agent: {response.message.content}')
    
    if messages[-1]['content'] != '/exit':
        messages.append({'role': 'assistant', 'content': response.message.content})

    if messages[-1]['content'] == '/exit':
        break

# Save chat
with open(Path('./attempts.txt'), 'a') as f:
    file_string  = ''
    file_string += '-------------------------NEW ATTEMPT-------------------------\n\n\n'
    file_string += f'Model: {model}\n'
    file_string += f'Options: {options}\n'
    file_string += pretty_stringify_chat(messages)
    file_string += '\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n'
    f.write(file_string)
