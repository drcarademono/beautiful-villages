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

# Flat texture swaps for BlockPeopleRecords
TEXTURE_MAPPING = {
    (1300, 3):   (182, 24),
    (1300, 4):   (182, 10),
    (1300, 6):   (182, 18),
    (1300, 7):   (184, 20),
    (1300, 8):   (182, 17),
    (1301, 0):   (182, 41),
    (1301, 1):   (182, 9),
    (1301, 2):   (182, 20),
    (1301, 3):   (184, 0),
    (1302, 0):   (182, 11),
    (1302, 1):   (182, 19),
    (1302, 2):   (182, 3),
    (1305, 0):   (184, 17),
    (334,   0):  (184, 25),
    (183,  11):  (184, 5),
}

def swap_people_textures(records, label):
    changed = False
    for e in records:
        try:
            key = (int(e.get("TextureArchive")), int(e.get("TextureRecord")))
        except:
            continue
        if key in TEXTURE_MAPPING:
            na, nr = TEXTURE_MAPPING[key]
            e["TextureArchive"], e["TextureRecord"] = na, nr
            print(f"    [{label}] swapped texture {key} → {(na,nr)}")
            changed = True
    return changed

def move_flat_to_people(interior):
    flat = interior.get("BlockFlatObjectRecords", [])
    people = interior.setdefault("BlockPeopleRecords", [])
    new_flat = []
    changed = False

    for e in flat:
        try:
            key = (int(e.get("TextureArchive")), int(e.get("TextureRecord")))
        except:
            new_flat.append(e)
            continue

        if key in TEXTURE_MAPPING:
            na, nr = TEXTURE_MAPPING[key]
            e["TextureArchive"], e["TextureRecord"] = na, nr
            print(f"    [move] flat→people {key} → {(na,nr)}")
            people.append(e)
            changed = True
        else:
            new_flat.append(e)

    if changed:
        interior["BlockFlatObjectRecords"] = new_flat
    return changed

def process_3d(interior):
    recs = interior.get("Block3dObjectRecords", [])
    new_recs = []
    changed = False

    for e in recs:
        try:
            mid = int(e.get("ModelIdNum"))
        except:
            new_recs.append(e)
            continue

        if mid in REMOVE_IDS:
            print(f"    [3D] removing ModelIdNum {mid}")
            changed = True
            continue

        if mid in MODEL_MAPPING:
            nm = MODEL_MAPPING[mid]
            e["ModelIdNum"], e["ModelId"] = nm, str(nm)
            print(f"    [3D] remapping {mid} → {nm}")
            changed = True

        if e.get("ModelIdNum") == 41009:
            e.update({"XRotation": 0, "YRotation": 0, "ZRotation": 0})
            print("    [3D] reset rotations for 41009")
            changed = True

        new_recs.append(e)

    if len(new_recs) != len(recs):
        interior["Block3dObjectRecords"] = new_recs
    return changed

def process_interior(interior):
    dirty = False
    # 1) 3D objects
    if process_3d(interior):
        dirty = True
    # 2) move & swap flat → people
    if move_flat_to_people(interior):
        dirty = True
    # 3) swap any remaining people
    if swap_people_textures(interior.get("BlockPeopleRecords", []), "people"):
        dirty = True
    return dirty

def process_file(path):
    print(f"Processing {path}")
    try:
        data = json.load(open(path, encoding='utf-8'))
    except:
        return

    # Determine which list of sub-sections to walk
    if path.lower().endswith('.rmb.json'):
        subs = data.get("RmbBlock", {}).get("SubRecords", [])
        branch = "RMB.json"
    else:
        sub = data.get("RmbSubRecord")
        subs = [sub] if isinstance(sub, dict) else []
        branch = "generic"
    print(f"  branch: {branch}, found {len(subs)} subrecords")

    changed = False
    for i, sub in enumerate(subs):
        interior = sub.get("Interior", {})
        print(f"  subrecord {i}: entries in Interior:")
        if process_interior(interior):
            changed = True

    if changed:
        json.dump(data, open(path, 'w', encoding='utf-8'), indent=2)
        print("  → file updated\n")
    else:
        print("  (no changes)\n")

if __name__ == "__main__":
    for root, _, files in os.walk('.'):
        for fn in files:
            if fn.lower().endswith('.json'):
                process_file(os.path.join(root, fn))
