import os
import re
import json
import random
import csv

# List of target ModelIds corresponding to DIEP house models
HOUSE_MODEL_IDS = {
    116, 117, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136,
    137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151,
    152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 200, 201, 202,
    203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 320, 321,
    324, 326, 327, 328, 329, 330, 332, 334, 335, 336, 337, 338, 339, 340, 421, 535,
    538, 539, 541, 543, 544, 546, 547, 548, 549, 551, 552, 559, 560, 562, 563,
    601, 602, 605, 606, 608, 610, 614, 658, 659, 663, 702, 704, 705, 707, 708,
    709
}

def preprocess_json(raw, placeholder="__BACKSLASH__"):
    return raw.replace("\\", placeholder)

def postprocess_json(raw, placeholder="__BACKSLASH__"):
    return raw.replace(placeholder, "\\")

def load_json_file(path, placeholder="__BACKSLASH__"):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            return json.loads(preprocess_json(text, placeholder))
    except Exception as e:
        print(f"Error loading JSON '{path}': {e}")
        return None

def save_json_file(path, data, placeholder="__BACKSLASH__"):
    try:
        dumped = json.dumps(data, indent=4)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(postprocess_json(dumped, placeholder))
    except Exception as e:
        print(f"Error saving JSON '{path}': {e}")

def replace_with_house(rmb_data, idx, house_data):
    bdl = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    srs = rmb_data["RmbBlock"].get("SubRecords", [])
    if idx >= len(bdl) or idx >= len(srs):
        return
    orig_b = bdl[idx]
    bdl[idx] = {
        "FactionId":    house_data.get("FactionId",   orig_b.get("FactionId")),
        "BuildingType": house_data.get("BuildingType",orig_b.get("BuildingType")),
        "Quality":      house_data.get("Quality",     orig_b.get("Quality")),
        "NameSeed":     house_data.get("NameSeed",    orig_b.get("NameSeed")),
    }
    if orig_b.get("FactionId") != 0:
        bdl[idx]["FactionId"] = orig_b.get("FactionId")
    orig_sr = srs[idx]
    upd_sr = orig_sr.copy()
    if "Interior" in orig_sr and "RmbSubRecord" in house_data:
        upd_sr["Interior"] = house_data["RmbSubRecord"]["Interior"]
    srs[idx] = upd_sr

def load_mod_list(dfmod_filename):
    data = load_json_file(dfmod_filename)
    files = set()
    if data and "Files" in data:
        for path in data["Files"]:
            base = re.split(r"[\\/]", path)[-1].lower()
            if base.endswith(".rmb.json"):
                files.add(base)
    return files

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def process_rmb_files(buildings_dir="buildings", diep_dir="diep"):
    # Load mod-listed RMB filenames (lowercased)
    mod_rmbs = set()
    for modfile in ("beautiful-cities.dfmod.json", "beautiful-villages.dfmod.json"):
        if os.path.isfile(modfile):
            mod_rmbs |= load_mod_list(modfile)

    # Group DIEP files by ModelId
    diep_by_model = {}
    for fn in os.listdir(diep_dir):
        if fn.endswith(".json") and not fn.endswith(".meta"):
            m = re.match(r"diep-(\d+)-\d+\.json$", fn)
            if m:
                mid = int(m.group(1))
                if mid in HOUSE_MODEL_IDS:
                    diep_by_model.setdefault(mid, []).append(os.path.join(diep_dir, fn))

    mappings = []  # (newFilename, originalDiepFile)

    for rmb_file in sorted(os.listdir(), key=natural_key):
        if not rmb_file.endswith(".RMB.json") or rmb_file.endswith(".meta"):
            continue

        print(f"Processing: {rmb_file}")
        rmb_data = load_json_file(rmb_file)
        if not rmb_data:
            continue

        rmb_index = rmb_data.get("Index")
        rmb_name = rmb_data.get("Name", "").strip()
        if rmb_index is None or not rmb_name:
            print(f"Skipping '{rmb_file}' due to missing header info.")
            continue

        subs = rmb_data.get("RmbBlock", {}).get("SubRecords", [])
        for i, sub in enumerate(subs):
            ext = sub.get("Exterior", {})
            recs = ext.get("Block3dObjectRecords", [])
            for rec in recs:
                mid = int(rec.get("ModelIdNum", rec.get("ModelId", -1)))
                if mid in HOUSE_MODEL_IDS and mid in diep_by_model:
                    # skip if existing building file
                    pattern = f"{rmb_file[:-5]}-*-building{i}.json"
                    if any(re.fullmatch(pattern, f) for f in os.listdir(buildings_dir) if not f.endswith(".meta")):
                        break
                    choice = random.choice(diep_by_model[mid])
                    house_data = load_json_file(choice)
                    if house_data:
                        replace_with_house(rmb_data, i, house_data)
                        # record only if this RMB is in the mod lists
                        if rmb_file.lower() in mod_rmbs:
                            new_filename = f"{rmb_name}-{rmb_index}-building{i}.json"
                            mappings.append((new_filename, os.path.basename(choice)))
                    break

        save_json_file(rmb_file, rmb_data)

    # write CSV
    with open("bcbv_diep_mappings.csv", "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(["NewFilename", "OriginalDiepFile"])
        for newfn, orig in sorted(mappings, key=lambda x: natural_key(x[0])):
            writer.writerow([newfn, orig])

if __name__ == "__main__":
    process_rmb_files()

