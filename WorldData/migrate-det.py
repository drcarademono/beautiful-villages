import os
import json
import re

def preprocess_json(raw_content, placeholder="__BACKSLASH__"):
    # Replace backslashes
    content = raw_content.replace("\\", placeholder)
    
    # Remove trailing commas in arrays and objects
    content = re.sub(r',\s*([\]}])', r'\1', content)
    
    return content

def postprocess_json(processed_content, placeholder="__BACKSLASH__"):
    return processed_content.replace(placeholder, "\\")

def load_json_file(filepath, placeholder="__BACKSLASH__"):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file), False  # Not preprocessed
    except json.JSONDecodeError:
        # Fallback: sanitize and try again
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                raw = file.read()
                processed = preprocess_json(raw, placeholder)
                return json.loads(processed), True  # Preprocessed version
        except Exception as e:
            print(f"Failed to preprocess JSON in '{filepath}': {e}")
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
    return None, False

def save_json_file(filepath, data, placeholder="__BACKSLASH__"):
    try:
        dumped = json.dumps(data, indent=4)
        restored = postprocess_json(dumped, placeholder)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(restored)
        print(f"✅ Updated: {filepath}")
    except Exception as e:
        print(f"❌ Error saving file '{filepath}': {e}")

def update_texture_archives(obj):
    changed = False
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "TextureArchive" and isinstance(value, int) and 1002 <= value <= 1070:
                obj[key] = value + 9000
                changed = True
            else:
                changed |= update_texture_archives(value)
    elif isinstance(obj, list):
        for item in obj:
            changed |= update_texture_archives(item)
    return changed

def process_directory_recursively(root_dir="."):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".json") and not filename.endswith(".meta"):
                filepath = os.path.join(dirpath, filename)
                data, was_preprocessed = load_json_file(filepath)
                if not data:
                    continue

                changed = update_texture_archives(data)
                if changed:
                    save_json_file(filepath, data)
                elif was_preprocessed:
                    # If we only fixed escapes but didn't change archives, still re-save to correct JSON
                    save_json_file(filepath, data)

if __name__ == "__main__":
    process_directory_recursively()

