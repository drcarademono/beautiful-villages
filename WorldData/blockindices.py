import os
import json

# Set up directories
main_directory = os.getcwd()  # Current directory
vanilla_subdir = os.path.join(main_directory, 'vanillarmbs')

# Ensure the vanilla directory exists
if not os.path.exists(vanilla_subdir):
    print(f"Error: '{vanilla_subdir}' does not exist.")
    exit()

# Initialize the starting Index
new_index = 2000

# Get a sorted list of all *.RMB.json files in the main directory
json_files = sorted([f for f in os.listdir(main_directory) if f.endswith('.RMB.json')])

for file_name in json_files:
    # Check if the file exists in the vanilla subdirectory
    vanilla_file_path = os.path.join(vanilla_subdir, file_name)
    if os.path.exists(vanilla_file_path):
        continue  # Skip if it exists in vanillarmbs

    # Process the file
    file_path = os.path.join(main_directory, file_name)
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Assign the new Index value
        if "Index" in data:
            data["Index"] = new_index
        else:
            print(f"Error: 'Index' field not found in {file_name}. Skipping file.")
            continue

        # Write the updated JSON back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

        # Print the processed file name and assigned Index
        print(f"Processed: {file_name}, Assigned Index: {new_index}")

        # Increment the Index
        new_index += 1

    except Exception as e:
        print(f"Error processing {file_name}: {e}")

