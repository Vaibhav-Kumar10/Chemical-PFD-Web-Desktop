import os
import json
import csv

def clean_string(s):
    return s.lower().translate(str.maketrans("", "", " ,_/-()"))

def load_label_data(base_dir):
    label_data = {}
    try:
        csv_path = os.path.join(base_dir, "ui", "assets", "Component_Details.csv")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get("object", "").strip() or row.get("name", "").strip()
                if not key:
                    continue

                label_data[clean_string(key)] = {
                    "legend": row.get("legend", "").strip(),
                    "suffix": row.get("suffix", "").strip(),
                    "count": 0
                }
    except Exception as e:
        print("Failed to load Component_Details.csv:", e)
    return label_data

def load_config(base_dir):
    component_config = {}
    try:
        path = os.path.join(base_dir, "ui", "assets", "grips.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                component_config[item["component"]] = item
    except Exception as e:
        print("Failed to load grips.json:", e)
    return component_config

def find_svg_path(name, base_dir):
    ID_MAP = {
        'Exchanger905': "905Exchanger",
        'KettleReboiler907': "907Kettle Reboiler",
        'OneCellFiredHeaterFurnace': "One Cell Fired Heater, Furnace",
        'TwoCellFiredHeaterFurnace': "Two Cell Fired Heater, Furnace"
    }
    name = ID_MAP.get(name, name)
    
    svg_dir = os.path.join(base_dir, "ui", "assets", "svg")
    target = clean_string(name)

    if not os.path.exists(svg_dir):
        print(f"SVG directory missing: {svg_dir}")
        return None

    for root, _, files in os.walk(svg_dir):
        for f in files:
            if not f.lower().endswith(".svg"):
                continue

            fname = f[:-4]
            # Direct match
            if fname == name:
                return os.path.join(root, f)
            # Clean match
            if clean_string(fname) == target:
                return os.path.join(root, f)

    print(f"No SVG found for: {name}")
    return None

def get_component_config_by_name(name, component_config):
    ID_MAP = {
        'Exchanger905': "905Exchanger",
        'KettleReboiler907': "907Kettle Reboiler",
        'OneCellFiredHeaterFurnace': "One Cell Fired Heater",
        'TwoCellFiredHeaterFurnace': "Two Cell Fired Heater"
    }
    name = ID_MAP.get(name, name)

    if name in component_config:
        return component_config[name]

    target = clean_string(name)
    for key, cfg in component_config.items():
        if clean_string(key) == target:
            return cfg

    return {}
