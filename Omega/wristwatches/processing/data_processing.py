import re

import numpy as np
import pandas as pd

# This class is used to process the raw wristwatch data

# Load the CSV file
data = pd.read_csv("../crawling/wristwatch_data.csv", low_memory=False, dtype=str)

data["Akumulátor"] = data["Akumulátor"].fillna("Ne")
data["Funkce"] = data["Funkce"].fillna("Ne")

# Define the required columns
required_columns = [
    "Značka", "Určení", "Pohon",
    "Materiál pouzdra", "Materiál sklíčka",
    "Použití", "Číselník", "Tvar pouzdra",
    "Baterie", "Původ", "Strojek", "Akumulátor",
    "Barva náramku", "Barva číselníku", "Funkce",
    "Cena", "Vodotěsnost", "Rozměr pouzdra", "Hmotnost"
]

# Drop rows with missing values in the required columns
filtered_data = data.dropna(subset=required_columns)

# Select only the required columns
filtered_data = filtered_data[required_columns]

# Define prefixes to remove
prefixes = ["Pánské", "Dámské", "Unisex", "Dětské"]

def extract_numeric(value, round_value=True):
    """Extracts numeric values from a string, replacing ',' with '.', converting to float, and rounding if needed."""
    if isinstance(value, str):
        cleaned_value = re.sub(r"[^\d.,]", "", value)  # Keep only digits, dots, and commas
        cleaned_value = cleaned_value.replace(",", ".")  # Convert commas to dots for decimals

        try:
            num = float(cleaned_value)
            return round(num) if round_value else num  # Round if specified
        except ValueError:
            return np.nan  # If conversion fails, return NaN
    return np.nan



# Apply cleaning functions to relevant columns
filtered_data["Cena"] = filtered_data["Cena"].apply(extract_numeric)
filtered_data["Vodotěsnost"] = filtered_data["Vodotěsnost"].apply(extract_numeric)
filtered_data["Rozměr pouzdra"] = filtered_data["Rozměr pouzdra"].apply(extract_numeric)
filtered_data["Hmotnost"] = filtered_data["Hmotnost"].apply(extract_numeric)


# Save the cleaned dataset
filtered_data.to_csv("resulting data/cleaned_wristwatch_data.csv", index=False, encoding="utf-8")

print(f"Original dataset: {len(data)} rows, {len(data.columns)} columns")
print(f"Filtered dataset: {len(filtered_data)} rows, {len(filtered_data.columns)} columns")
