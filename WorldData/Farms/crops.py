import os
import json
import random
import re

# Directory containing the JSON files
directory = '.'

# Helper function to handle invalid escape sequences
def load_json_robust(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Attempt to fix invalid escapes
        with open(file_path, 'r') as file:
            data = file.read()
            # Replace invalid escapes with their literal characters
            fixed_data = re.sub(r'\\([^"\\bfnrtu])', r'\\\\\1', data)
            try:
                return json.loads(fixed_data)
            except json.JSONDecodeError:
                print(f"Could not fix JSON decoding in file: {file_path}")
                return None

# Recursive function to update TextureRecord if conditions are met
def update_texture_record(data):
    global modified
    if isinstance(data, dict):
        # Check if TextureArchive is 1037 and TextureRecord > 11
        if data.get("TextureArchive") == 1037 and data.get("TextureRecord", 0) > 11:
            data["TextureRecord"] = random.randint(0, 11)
            modified = True
        # Recursively check nested dictionaries
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                update_texture_record(value)
    elif isinstance(data, list):
        # Recursively check each element in the list
        for item in data:
            update_texture_record(item)

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)

        # Read the JSON content with robustness
        data = load_json_robust(filepath)
        if data is None:
            continue

        modified = False

        # Update TextureRecord throughout the JSON
        update_texture_record(data)

        # Write changes back to the JSON file if modified
        if modified:
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Modified: {filename}")

