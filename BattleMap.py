import json

class Battlemap:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]  # 2D grid
        self.entities = {}  # Dictionary to store entity IDs and their positions

    def add_entity(self, entity_id, x, y):
        if self.is_valid_position({'x': x, 'y': y}):
            # Store the position of the entity by its ID
            self.entities[entity_id] = {'x': x, 'y': y}
            self.grid[y][x] = entity_id  # Mark entity ID on the battlemap
        else:
            print(f"Invalid position for entity {entity_id} at ({x}, {y})")

    def move_entity(self, entity_id, new_x, new_y):
        if entity_id in self.entities and self.is_valid_position({'x': new_x, 'y': new_y}):
            # Remove entity from old position
            old_x, old_y = self.entities[entity_id]['x'], self.entities[entity_id]['y']
            self.grid[old_y][old_x] = None  

            # Update entity position
            self.entities[entity_id] = {'x': new_x, 'y': new_y}
            self.grid[new_y][new_x] = entity_id  # Mark new position
        else:
            print(f"Invalid move for entity {entity_id} to position ({new_x}, {new_y})")

    def is_valid_position(self, position):
        # Ensure the position is within the bounds of the grid
        return 0 <= position['x'] < self.width and 0 <= position['y'] < self.height

    def get_entity_position(self, entity_id):
        # Get the position of a given entity by its ID
        if entity_id in self.entities:
            return self.entities[entity_id]
        return None

    def print_positions(self, entity_ids):
        # Display the positions of the given entity IDs
        for entity_id in entity_ids:
            position = self.get_entity_position(entity_id)
            if position:
                print(f"Entity {entity_id} is at position {position}")
            else:
                print(f"Entity {entity_id} not found on the battlemap.")

    def save_to_file(self, filename):
        data = {
            'width': self.width,
            'height': self.height,
            'entities': [{'entity_id': entity_id, 'position': position} for entity_id, position in self.entities.items()]
        }
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Battlemap successfully saved to {filename}")
        except TypeError as e:
            print(f"Error serializing data: {e}")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.width = data['width']
            self.height = data['height']
            self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
            self.entities = {}

            for entity_data in data['entities']:
                entity_id = entity_data['entity_id']
                position = entity_data['position']
                self.add_entity(entity_id, position['x'], position['y'])

            print(f"Loaded battlemap with {len(self.entities)} entities.")
        except json.JSONDecodeError as e:
            print(f"Error reading the JSON file: {e}")
