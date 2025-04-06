import csv
import json

# This class is used to transfer the cleaned wristwatch data from CSV to JSON format

# File paths
csv_file_path = "resulting data/cleaned_wristwatch_data.csv"
json_mapping_path = "resulting data/multiple_choice_features_cleaned.json"
output_json_path = "resulting data/converted_wristwatch_data.json"

# Load the multi-label feature mapping
with open(json_mapping_path, "r", encoding="utf-8") as f:
    feature_mappings = json.load(f)

multi_label_features = set(feature_mappings.keys())

# Define numeric fields to convert
numeric_fields = {"Vodotěsnost", "Rozměr pouzdra", "Hmotnost", "Cena"}

def try_parse_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# Read CSV and convert to structured JSON
output_data = []
with open(csv_file_path, "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        converted_row = {}
        for key, value in row.items():
            if key in multi_label_features:
                # Split multi-labeled string by comma
                labels = [v.strip() for v in value.split(",") if v.strip()]
                converted_row[key] = labels
            elif key in numeric_fields:
                converted_row[key] = try_parse_number(value)
            else:
                converted_row[key] = value.strip() if isinstance(value, str) else value
        output_data.append(converted_row)

# Write the structured JSON output
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Conversion complete. Output saved to {output_json_path}")
