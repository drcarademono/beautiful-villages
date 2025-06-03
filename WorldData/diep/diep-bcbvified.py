#!/usr/bin/env python3
import os
import json

# IDs to remove entirely from Block3dObjectRecords
REMOVE_IDS = {
    45078, 45104, 45105, 45131,
    45079, 45106, 45107, 45132,
    45080, 45108, 45109, 45133
}

# ModelIdNum remapping for Block3dObjectRecords
MODEL_MAPPING = {
    # → 41000 (Beds)
    #42069: 41000, 42072: 41000, 42075: 41000,
    #42078: 41000, 42081: 41000, 42084: 41000,
    # → 41001
    #42070: 41001, 42073: 41001, 42076: 41001,
    #42079: 41001, 42082: 41001, 42085: 41001,
    # → 41002
    #42071: 41002, 42074: 41002, 42077: 41002,
    #42080: 41002, 42083: 41002, 42086: 41002,
    # additional remaps
    69438: 69432, 69439: 69432,
    69442: 69441, 69443: 69445,
    69466: 41009,
}

# Texture swaps for BlockPeopleRecords: (Archive, Record) → (newArchive, newRecord)
PEOPLE_TEXTURE_MAPPING = {
    (1300, 3):  (182, 20),
    (1300, 4):  (182, 10),
    (1300, 6):  (182, 18),
    (1300, 7):  (184, 20),
    (1300, 8):  (182, 17),
    (1301, 0):  (182, 41),
    (1301, 1):  (182,  9),
    (1301, 2):  (182, 20),
    (1302, 0):  (182, 11),
    (1302, 1):  (182, 20),
    (1302, 2):  (182,  3),
    (1305, 0):  (182, 20),
    (334,   0): (184, 25),
    (183,  11): (184,  5),
}

def process_people_records(records):
    changed = False
    for entry in records:
        ta = entry.get("TextureArchive")
        tr = entry.get("TextureRecord")
        try:
            key = (int(ta), int(tr))
        except (TypeError, ValueError):
            continue

        if key in PEOPLE_TEXTURE_MAPPING:
            new_ta, new_tr = PEOPLE_TEXTURE_MAPPING[key]
            entry["TextureArchive"] = new_ta
            entry["TextureRecord"]  = new_tr
            # debug: comment out if noisy
            print(f"  swapped person texture {key} → {(new_ta,new_tr)}")
            changed = True
    return changed

def process_rmb_json(data):
    changed = False
    rmb = data.get("RmbBlock")
    if not isinstance(rmb, dict):
        return False

    for sub in rmb.get("SubRecords", []):
        interior = sub.get("Interior", {})

        # 1) 3D objects (unchanged)
        recs3d = interior.get("Block3dObjectRecords", [])
        new3d = []
        for e in recs3d:
            mid = e.get("ModelIdNum")
            try:
                mid_i = int(mid)
            except (TypeError, ValueError):
                new3d.append(e)
                continue

            if mid_i in REMOVE_IDS:
                changed = True
                continue
            if mid_i in MODEL_MAPPING:
                e["ModelIdNum"] = MODEL_MAPPING[mid_i]
                e["ModelId"]    = str(MODEL_MAPPING[mid_i])
                changed = True

            if e.get("ModelIdNum") == 41009:
                e["XRotation"] = 0
                e["YRotation"] = 0
                e["ZRotation"] = 0
                changed = True

            new3d.append(e)
        if len(new3d) != len(recs3d):
            interior["Block3dObjectRecords"] = new3d

        # 2) People textures
        if process_people_records(interior.get("BlockPeopleRecords", [])):
            changed = True

    return changed

def process_generic_json(data):
    changed = False
    subrec = data.get("RmbSubRecord")
    if not isinstance(subrec, dict):
        return False

    interior = subrec.get("Interior", {})

    # 1) 3D objects
    recs3d = interior.get("Block3dObjectRecords", [])
    new3d = []
    for e in recs3d:
        mid = e.get("ModelIdNum")
        try:
            mid_i = int(mid)
        except (TypeError, ValueError):
            new3d.append(e)
            continue

        if mid_i in REMOVE_IDS:
            changed = True
            continue
        if mid_i in MODEL_MAPPING:
            e["ModelIdNum"] = MODEL_MAPPING[mid_i]
            e["ModelId"]    = str(MODEL_MAPPING[mid_i])
            changed = True

        if e.get("ModelIdNum") == 41009:
            e["XRotation"] = 0
            e["YRotation"] = 0
            e["ZRotation"] = 0
            changed = True

        new3d.append(e)
    if len(new3d) != len(recs3d):
        interior["Block3dObjectRecords"] = new3d

    # 2) People textures
    if process_people_records(interior.get("BlockPeopleRecords", [])):
        changed = True

    return changed

def process_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return

    print(f"Scanning {path}…")
    if path.lower().endswith(".rmb.json"):
        dirty = process_rmb_json(data)
    else:
        dirty = process_generic_json(data)

    if dirty:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"→ Updated {path}")

if __name__ == "__main__":
    for root, _, files in os.walk('.'):
        for fn in files:
            if fn.lower().endswith('.json'):
                process_file(os.path.join(root, fn))

