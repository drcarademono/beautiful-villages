import os
import json
import pandas as pd
import re

def remove_entries(json_data):
    # Define the ModelIdNum values to be removed
    remove_ids = {52990, 52991, 45074, 45075, 45076, 45077}
    
    def filter_records(records):
        """Helper function to filter out records with specified ModelIdNum values."""
        return [record for record in records if record.get('ModelIdNum') not in remove_ids]

    # Check and filter records in RmbBlock.SubRecords
    if "RmbBlock" in json_data and "SubRecords" in json_data["RmbBlock"]:
        for sub_record in json_data["RmbBlock"]["SubRecords"]:
            if "Exterior" in sub_record:
                sub_record["Exterior"]["Block3dObjectRecords"] = filter_records(sub_record["Exterior"]["Block3dObjectRecords"])
            if "Interior" in sub_record:
                sub_record["Interior"]["Block3dObjectRecords"] = filter_records(sub_record["Interior"]["Block3dObjectRecords"])

    # Check and filter records in RmbBlock.Misc3dObjectRecords
    if "RmbBlock" in json_data and "Misc3dObjectRecords" in json_data["RmbBlock"]:
        json_data["RmbBlock"]["Misc3dObjectRecords"] = filter_records(json_data["RmbBlock"]["Misc3dObjectRecords"])
    
    return json_data

def add_new_entries(json_data, building_dimensions):
    # Convert index to string to ensure consistency in comparisons
    building_dimensions.index = building_dimensions.index.map(str)
    
    def find_max_y_and_rotation(exterior_records):
        max_y = float('-inf')
        max_y_rotation = 0
        for record in exterior_records:
            model_id = record.get("ModelId")
            if model_id and str(model_id) in building_dimensions.index:
                y_value = building_dimensions.loc[str(model_id), "Y"]
                if y_value > max_y:
                    max_y = y_value
                    max_y_rotation = record.get("YRotation", 0)
        return max_y, max_y_rotation

    # Check SubRecords for matching Interior Block3dObjectRecords
    if "RmbBlock" in json_data and "SubRecords" in json_data["RmbBlock"]:
        for sub_record in json_data["RmbBlock"]["SubRecords"]:
            if "Interior" in sub_record and "Exterior" in sub_record:
                interior_records = sub_record["Interior"]["Block3dObjectRecords"]
                exterior_records = sub_record["Exterior"]["Block3dObjectRecords"]

                # Find if there are any matching Interior records
                matching_interior = any(record.get("ModelIdNum") in {41116, 41117} for record in interior_records)
                
                if matching_interior:
                    # Find max Y value and rotation from exterior records
                    max_y_value, max_y_rotation = find_max_y_and_rotation(exterior_records)

                    # Add new entries to Exterior if matching Interior entries are found
                    for interior_record in interior_records:
                        if interior_record.get("ModelIdNum") in {41116, 41117}:
                            new_record_52991 = interior_record.copy()
                            new_record_52991["ModelId"] = "52991"
                            new_record_52991["ModelIdNum"] = 52991
                            new_record_52991["ObjectType"] = 4
                            new_record_52991["YRotation"] = max_y_rotation
                            if max_y_value != float('-inf'):
                                if max_y_value <= 220:
                                    new_record_52991["YPos"] = int(-(max_y_value + 20))
                                elif max_y_value >= 300:
                                    new_record_52991["YPos"] = int(-(max_y_value - 80))
                                else:
                                    new_record_52991["YPos"] = int(-(max_y_value))
                            else:
                                new_record_52991["YPos"] = 0  # Default value if no valid max Y value is found
                            
                            exterior_records.append(new_record_52991)
                            
                            new_record_45077 = new_record_52991.copy()
                            new_record_45077["ModelId"] = "45077"
                            new_record_45077["ModelIdNum"] = 45077
                            new_record_45077["YPos"] += 129
                            new_record_45077["XScale"] = 0.9
                            new_record_45077["ZScale"] = 0.9
                            exterior_records.append(new_record_45077)
                            
                            current_y_pos = new_record_45077["YPos"]
                            while current_y_pos <= 0:
                                new_record_45076 = new_record_45077.copy()
                                new_record_45076["ModelId"] = "45076"
                                new_record_45076["ModelIdNum"] = 45076
                                new_record_45076["YPos"] = current_y_pos + 114
                                new_record_45076["XScale"] = 0.9
                                new_record_45076["ZScale"] = 0.9
                                exterior_records.append(new_record_45076)
                                
                                current_y_pos += 114
                                if current_y_pos > 0:
                                    break

                    # Update Num3dObjectRecords in the Exterior header
                    sub_record["Exterior"]["Header"]["Num3dObjectRecords"] = len(exterior_records)
    
    return json_data

# Function to escape invalid sequences
def sanitize_json_string(json_string):
    # Regex pattern to find invalid escape sequences
    pattern = re.compile(r'\\(?![btnfr"\\])')
    return pattern.sub(r'\\\\', json_string)

# Read the CSV file with comma separator and check for correct columns
try:
    building_dimensions = pd.read_csv('BuildingDimensions.csv')

    # Set ModelID as the index column if it exists
    if 'ModelId' in building_dimensions.columns:
        building_dimensions.set_index('ModelId', inplace=True)
    else:
        print("ModelId column not found in the CSV file. Columns available are:", building_dimensions.columns.tolist())
except Exception as e:
    print(f"Error reading CSV file: {e}")

# Process all JSON files in the current directory
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        print(f"Processing file: {filename}")  # Debug message
        try:
            with open(filename, 'r') as file:
                json_string = file.read()
                sanitized_string = sanitize_json_string(json_string)
                data = json.loads(sanitized_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file {filename}: {e}")
            continue
        
        # Process the data
        updated_data = remove_entries(data)
        updated_data = add_new_entries(updated_data, building_dimensions)
        
        # Save the updated JSON data
        with open(filename, 'w') as file:
            json.dump(updated_data, file, indent=4)

        print(f"Processed and updated: {filename}")

print("All JSON files processed.")

