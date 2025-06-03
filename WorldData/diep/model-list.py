import json
import os


def load_json_file(file_path):
    """
    Loads a JSON file.
    :param file_path: Path to the JSON file.
    :return: Parsed JSON data or None if the file couldn't be parsed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None


def extract_model_ids(file_path):
    """
    Extracts ModelId values from the RmbSubRecord > Exterior > Block3dObjectRecords array.
    :param file_path: Path to the building JSON file.
    :return: List of ModelId values or an empty list if not found.
    """
    data = load_json_file(file_path)
    if not data:
        return []

    try:
        block3d_object_records = (
            data.get("RmbSubRecord", {})
                .get("Exterior", {})
                .get("Block3dObjectRecords", [])
        )
        return [
            int(record.get("ModelId"))
            for record in block3d_object_records
            if "ModelId" in record and str(record.get("ModelId")).isdigit()
        ]
    except AttributeError:
        print(f"Error: Invalid structure in file '{file_path}'.")
        return []


def process_building_files(directory="."):
    """
    Processes all *building*.json files in the specified directory and extracts ModelId values.
    Limits ModelIds to those under 1000, and sorts them in numerical order.
    :param directory: Directory containing the building JSON files.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    building_files = [os.path.join(directory, file) for file in os.listdir(directory) if "building" in file and file.endswith(".json")]

    all_model_ids = []
    for file in building_files:
        print(f"Processing file: {file}")
        model_ids = extract_model_ids(file)
        all_model_ids.extend(model_ids)

    # Filter ModelIds under 1000 and sort them
    filtered_sorted_model_ids = sorted(set(mid for mid in all_model_ids if mid < 1000))

    # Output the results
    print("\nModelIds under 1000 (sorted):")
    for model_id in filtered_sorted_model_ids:
        print(model_id)


if __name__ == "__main__":
    process_building_files()

