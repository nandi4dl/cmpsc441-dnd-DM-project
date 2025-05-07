# **CMPSC 441**

# **AI DnD Dungeon Master Project Report**
**Anu Mallya, Alexander Harris, Jason Bollinger**

**RUN DnDDMModel.py  to run the system** 

**Section 1: Scenarios**
-   Tavern social encounters with diverse NPC dialogues.
-   Dungeon exploration with descriptions of rooms, items, and traps.
-   Combat resolution (attack rolls, damage calculation, hit/miss outcomes).
-   Complex NPC interactions (merchant bargaining, deceptive characters).
-   Detailed narration of player actions (stealth, persuasion attempts, lock-picking outcomes).
-   Automated dice rolls for skills, combat, and saves.
-   Real-time rules and spell effect look-ups.
-   Monster stat and lore retrieval during encounters.
-   Multi-stage puzzle solving and hint delivery.
-   Strategic enemy decisions (retreat, negotiation, flanking tactics).
-   Integrating previously established lore into current storytelling.
-   Dynamic map generation based on player exploration

**Section 2: Model Parameter Choice, Prompt Engineering**
Temperature: 1.0 (variable)
Max tokens: 100
Reasoning: The temperature has been set to be at a baseline of 1.0 but  is  variable based on the success or failure of player's dice rolls during skill checks. This is done to give the experience a more fantastical feeling, since the DM agent will hallucinate more and create more intriguing or fun scenarios the better the player rolls, to keep the player engaged and interested, and will push the player to keep playing hoping for good rolls each time, while also ensuring that the responses of the agent are not so long that it becomes boring to read and keep up with the DM agent.

The agent uses various tools to assist in creating immersive experiences for the player, for all aspects of the experience of playing DnD, such as combat.
DM Model Prompt: 
"You are a Dungeon Master running a D&D 5e campaign. Guide the player through character creation, combat encounters, inventory management, and storyline progression. Respond to player input, and dynamically update the battlemap, combat mechanics, and shop inventory. Use the tools for relevant tasks, like creating a battlemap, rolling for skill checks, and generating shop inventories."

Character Creation Prompt:
"You are a Dungeon Master helping a player create a D&D 5e character. Ask for character name, age, level, gender, description, background, class, race, and stats. Let the player assign stats using the standard array {15, 14, 13, 12, 10, 8} to the six abilities: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma. After stats are assigned, apply any racial bonuses (fetched via API). Fetch class features for the provided level and race traits (also fetched via API). Be sure to fetch **Human racial bonuses** and apply +1 to all stats. Display the racial traits, class features, and background options accordingly. Provide starter items based on class and background, including gear and gold. Ensure the racial and class bonuses are properly applied before proceeding with character creation. Only show the background options that fit with the character's background (e.g., for Entertainer). Be warm, friendly, and immersive in your approach."

**Section 3: Tools Usage**
The system utilizes multiple tool calls for various purposes such as:
- Creation of battlemaps
- Generating and displaying shop inventories
- Rolling skill checks
- Creating characters
- Combat CR calculation

**Section 4: Planning and Reasoning**
- The chosen model was Llama3.2:3b due to being entirely open source, and lightweight, and is versatile in text and image based tasks. Furthermore, it is the model with which we have the most experience.
- We used both a local as well as API based database for retrieval based tool calls to speed up the response times to simpler tasks like setting initial player inventories with basic items from the local database.
- We focused more tools on the battle and shopping system due to the fact that most DnD players spend more time using those systems than the character creation system.

**Section 5: RAG Implementation**
- API calls to existing database of DnD information (classes, items etc)
- Local list of basic starter items to retrieve and assign to created characters as well as accessible in shops

**Section 6: Additional Tools**
- API Calls to https://www.dnd5eapi.co to retrieve character relevant information