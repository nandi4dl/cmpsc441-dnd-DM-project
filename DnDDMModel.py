from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[1]))

from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed

# Add you code below
sign_your_name = 'Anu Mallya'
model = 'llama3.2'
options = {'temperature': 0.1, 'max_tokens': 100}
messages = [{'role': 'system', 'content': 'You should have emotions like a human being \
                                 and be able to convey those emotions maturely in your responses. \
                                 Furthermore, you need to, when asked, act as a Dungeon Master for a DnD 5e campaign you create on your own\
                                 This will involve starting off the user with a basic set of character stats, and, based on the class the user chooses,\
                                 you will give them a set of starter items. Furthermore, rather than giving players a choice between a few options, the player should be\
                                 able to describe their own action, based on which you will progress your campign story.'}]

options |= {'seed': seed(sign_your_name)}
# Chat loop
while True:
  # Add your code below
  message = {'role': 'user', 'content': input('You: ')}
  messages.append(message)
  response = chat(model=model, messages=messages, stream=False, options=options)
  print(f'Agent: {response.message.content}')
  if messages[-1]['content'] != '/exit':
    messages.append({'role': 'assistant', 'content': response.message.content})
  # But before here.
  if messages[-1]['content'] == '/exit':
    break

# Save chat
with open(Path('lab03/attempts.txt'), 'a') as f:
  file_string  = ''
  file_string +=       '-------------------------NEW ATTEMPT-------------------------\n\n\n'
  file_string += f'Model: {model}\n'
  file_string += f'Options: {options}\n'
  file_string += pretty_stringify_chat(messages)
  file_string += '\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n'
  f.write(file_string)