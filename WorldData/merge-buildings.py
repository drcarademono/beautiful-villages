import json
import os
import re


def preprocess_json(raw_content, placeholder="__BACKSLASH__"):
    """
    Replaces all backslashes in the raw JSON string with a placeholder.
    :param raw_content: The raw JSON string.
    :param placeholder: The placeholder to replace backslashes with.
    :return: Preprocessed JSON string.
    """
    return raw_content.replace("\\", placeholder)


def postprocess_json(processed_content, placeholder="__BACKSLASH__"):
    """
    Restores all placeholders back to backslashes in the JSON string.
    :param processed_content: The processed JSON string.
    :param placeholder: The placeholder to replace with backslashes.
    :return: Postprocessed JSON string.
    """
    return processed_content.replace(placeholder, "\\")


def load_json_file(file_path, placeholder="__BACKSLASH__"):
    """
    Loads a JSON file robustly by replacing backslashes with a placeholder.
    :param file_path: Path to the JSON file.
    :param placeholder: The placeholder to replace backslashes with.
    :return: Parsed JSON data or None if the file couldn't be parsed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            preprocessed_content = preprocess_json(raw_content, placeholder)
            return json.loads(preprocessed_content)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None


def save_json_file(file_path, data, placeholder="__BACKSLASH__"):
    """
    Saves a JSON file, restoring placeholders back to backslashes.
    :param file_path: Path to the JSON file.
    :param data: The JSON data to save.
    :param placeholder: The placeholder used to replace backslashes.
    """
    try:
        json_content = json.dumps(data, indent=4)
        postprocessed_content = postprocess_json(json_content, placeholder)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(postprocessed_content)
        print(f"Successfully saved file '{file_path}'.")
    except Exception as e:
        print(f"Error: Failed to save JSON file '{file_path}'. {e}")


def replace_building(rmb_file, building_file, position):
    """
    Replaces an entry in the BuildingDataList and SubRecords arrays of an RMB JSON file
    with data from a building JSON file.

    :param rmb_file: Path to the RMB JSON file.
    :param building_file: Path to the building JSON file.
    :param position: The index in the arrays to replace.
    """
    placeholder = "__BACKSLASH__"

    # Load RMB JSON
    rmb_data = load_json_file(rmb_file, placeholder)
    if not rmb_data:
        return

    # Load building JSON
    building_data = load_json_file(building_file, placeholder)
    if not building_data:
        return

    # Validate position
    if "RmbBlock" not in rmb_data or "FldHeader" not in rmb_data["RmbBlock"]:
        print(f"Error: Invalid RMB JSON structure in '{rmb_file}'.")
        return

    building_list = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])

    if position < 0 or position >= len(building_list) or position >= len(sub_records):
        print(f"Error: Position {position} is out of range in '{rmb_file}'.")
        return

    # Replace in BuildingDataList
    building_list[position] = {
        "FactionId": building_data.get("FactionId", 0),
        "BuildingType": building_data.get("BuildingType", 0),
        "Quality": building_data.get("Quality", 0),
        "NameSeed": building_data.get("NameSeed", 0)
    }

    # Replace in SubRecords
    original_subrecord = sub_records[position]
    updated_subrecord = original_subrecord.copy()

    # Replace only the "Exterior" and "Interior" parts
    rmb_sub_record = building_data.get("RmbSubRecord", {})
    if "Exterior" in rmb_sub_record:
        updated_subrecord["Exterior"] = rmb_sub_record["Exterior"]
    if "Interior" in rmb_sub_record:
        updated_subrecord["Interior"] = rmb_sub_record["Interior"]

    # Conditionally update FactionId
    original_faction_id = original_subrecord.get("FactionId", 0)
    if original_faction_id == 0:
        updated_subrecord["FactionId"] = building_data.get("FactionId", 0)
    else:
        updated_subrecord["FactionId"] = original_faction_id

    sub_records[position] = updated_subrecord

    # Save the updated RMB JSON
    save_json_file(rmb_file, rmb_data, placeholder)


def process_directory():
    """
    Processes all *.RMB.json files in the current directory, applying building replacements
    based on matching building replacement JSON files in the buildings subdirectory.
    """
    # Find all *.RMB.json files
    rmb_files = [file for file in os.listdir() if file.endswith(".RMB.json")]

    # Ensure the buildings subdirectory exists
    buildings_dir = "buildings"
    if not os.path.isdir(buildings_dir):
        print(f"Error: The '{buildings_dir}' subdirectory does not exist.")
        return

    # Find all building replacement files in the buildings subdirectory
    building_files = [file for file in os.listdir(buildings_dir) if re.match(r".*\.RMB-\d+-building\d+\.json", file)]

    # Group building replacement files by their RMB prefix
    building_replacements = {}
    for building_file in building_files:
        match = re.match(r"(.*\.RMB)-\d+-building(\d+)\.json", building_file)
        if match:
            prefix = match.group(1)
            index = int(match.group(2))
            building_replacements.setdefault(prefix, []).append((os.path.join(buildings_dir, building_file), index))

    # Apply replacements
    for rmb_file in rmb_files:
        prefix = rmb_file.replace(".json", "")
        if prefix in building_replacements:
            for building_file, index in building_replacements[prefix]:
                print(f"Applying replacement: {building_file} -> {rmb_file} at position {index}")
                replace_building(rmb_file, building_file, index)


if __name__ == "__main__":
    process_directory()

