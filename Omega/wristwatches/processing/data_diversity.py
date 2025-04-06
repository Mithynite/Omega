import pandas as pd
import json
import re

# Load the dataset
file_path = "resulting data/cleaned_wristwatch_data.csv"
df = pd.read_csv(file_path)

# Columns to analyze
columns_to_extract = [
    "Značka", "Určení", "Pohon",
    "Materiál pouzdra", "Materiál sklíčka",
    "Číselník", "Tvar pouzdra","Baterie",
    "Původ", "Strojek", "Akumulátor",
    "Barva náramku", "Barva číselníku", "Funkce"
]

# Pattern to split on multiple delimiters
split_pattern = re.compile(r"[,/]| a | i ")

# Dictionary to store unique values and their counts
unique_values = {}

for column in columns_to_extract:
    if column not in df.columns:
        continue

    # Initialize column dict
    column_counts = {}

    # Drop NA, cast to string, iterate rows
    for raw_value in df[column].dropna().astype(str):
        # Split value on delimiters
        for item in split_pattern.split(raw_value):
            item = item.strip().capitalize()
            if not item:
                continue
            if item in column_counts:
                column_counts[item] += 1
            else:
                column_counts[item] = 1

    # Add to global dict
    unique_values[column] = dict(sorted(column_counts.items(), key=lambda x: -x[1]))

# Save to JSON
output_file = "resulting data/multiple_choice_features_cleaned.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(unique_values, f, ensure_ascii=False, indent=4)

# Print results
for column, items in unique_values.items():
    print(f"\n{column}:")
    for value, count in items.items():
        print(f"  - {value} (appears {count} times)")
