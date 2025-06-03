import json
import os
import shutil

# List of ModelIds corresponding to houses for the DIEP project
DIEP_MODEL_IDS = {
    116, 117, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
    138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153,
    154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 200, 201, 202, 203, 204, 205,
    206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 320, 321, 324, 326, 327, 328,
    330, 332, 334, 335, 336, 337, 338, 339, 340, 421, 535, 538, 539, 541, 543, 544,
    546, 547, 548, 549, 552, 562, 602, 605, 606, 608, 610, 614, 658, 659, 663, 702,
    704, 705, 707, 708, 709
}

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None

def get_diep_model_id(data):
    try:
        block3d_object_records = (
            data.get("RmbSubRecord", {})
                .get("Exterior", {})
                .get("Block3dObjectRecords", [])
        )
        for record in block3d_object_records:
            model_id = int(record.get("ModelId", -1))
            if model_id in DIEP_MODEL_IDS:
                return model_id
    except Exception as e:
        print(f"Error processing data structure: {e}")
    return None

def process_building_files(directory=".", output_directory="diep"):
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    os.makedirs(output_directory, exist_ok=True)

    building_files = [file for file in os.listdir(directory) if "building" in file and file.endswith(".json")]
    diep_counts = {}

    for file in building_files:
        file_path = os.path.join(directory, file)
        print(f"Processing file: {file_path}")

        data = load_json_file(file_path)
        if not data:
            continue

        model_id = get_diep_model_id(data)
        if model_id is not None:
            count = diep_counts.get(model_id, 0)
            diep_counts[model_id] = count + 1

            new_filename = f"diep-{model_id:03d}-{count:02d}.json"
            new_file_path = os.path.join(output_directory, new_filename)

            shutil.move(file_path, new_file_path)
            print(f"Moved file to: {new_file_path}")

# Execute the function
process_building_files()

