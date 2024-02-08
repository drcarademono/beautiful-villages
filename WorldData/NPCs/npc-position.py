import json
import os
import random

def update_positions(data, unique_positions, position_counter):
    """
    Recursively update positions for all objects with a Position field.
    """
    if isinstance(data, dict):
        # Check if this dict has the Position we're looking to update
        if "Position" in data:
            data["Position"] = unique_positions[position_counter[0]]
            position_counter[0] += 1  # Update the counter
        # Recursively update nested dictionaries
        for key in data:
            update_positions(data[key], unique_positions, position_counter)
    elif isinstance(data, list):
        # Recursively update items in the list
        for item in data:
            update_positions(item, unique_positions, position_counter)

def process_json_file(file_path, unique_positions, position_counter):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Start updating positions
    update_positions(data, unique_positions, position_counter)

    # Save the modified data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def process_all_json_files(directory):
    # Prepare a list of unique positions to use. Adjust the size as needed.
    # Ensure you have enough unique values for the number of position fields to update.
    unique_positions = random.sample(range(5000, 10001), 5000)
    position_counter = [0]  # Use a list as a mutable counter

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            process_json_file(os.path.join(directory, filename), unique_positions, position_counter)

# Process all JSON files in the current directory
process_all_json_files('.')

