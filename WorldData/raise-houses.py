#!/usr/bin/env python3
import os
import re

def process_file(path):
    lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
    out = []
    ctx = []  # stack of (context_name, indent)

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # ---- enter contexts ----
        if stripped.startswith('"RmbBlock"') and stripped.rstrip().endswith('{'):
            ctx.append(("RmbBlock", indent))

        elif stripped.startswith('"SubRecords"') and stripped.rstrip().endswith('['):
            if ctx and ctx[-1][0] == "RmbBlock":
                ctx.append(("SubRecords", indent))

        elif stripped.startswith('"Exterior"') and stripped.rstrip().endswith('{'):
            if ctx and ctx[-1][0] == "SubRecords":
                ctx.append(("Exterior", indent))

        elif stripped.startswith('"Block3dObjectRecords"') and stripped.rstrip().endswith('['):
            if ctx and ctx[-1][0] == "Exterior":
                ctx.append(("Block3dObjectRecords", indent))

        # ---- only inside Exterior → Block3dObjectRecords ----
        if ctx and ctx[-1][0] == "Block3dObjectRecords":
            # change any YPos: 2 to YPos: 0
            new_line = re.sub(r'("YPos"\s*:\s*)2\b', r'\1 0', line)
            if new_line is not line:
                line = new_line

        out.append(line)

        # ---- exit contexts ----
        stripped_no_comma = stripped.rstrip().rstrip(',')
        if ctx:
            name, start_indent = ctx[-1]
            # exit array contexts
            if name in ("Block3dObjectRecords", "SubRecords") and stripped_no_comma.startswith(']') and indent == start_indent:
                ctx.pop()
            # exit object contexts
            elif name in ("Exterior", "RmbBlock") and stripped_no_comma.startswith('}') and indent == start_indent:
                ctx.pop()

    # write changes back
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Reversed: {path}")

def main():
    for root, _, files in os.walk("."):
        for fn in files:
            if fn.endswith(".RMB.json"):
                process_file(os.path.join(root, fn))

if __name__ == "__main__":
    main()

