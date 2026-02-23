import argparse

import pandas as pd
import numpy as np
import os
import re

# Anything not in the normal charset of things will be replaced with nothing
def clean_text(text):
    text = str(text)  # Ensure it's a string
    # Remove newlines and tabs
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Remove any non-alphanumeric characters except spaces and basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def row_to_ditto_string(row, left_cols, right_cols, label_col):
    """
    Converts a single row into the Ditto string format:
    COL col1 VAL val1 ... 	COL col1 VAL val1 ... 	LABEL
    """
    left_parts = []
    for col in left_cols:
        # Extract the original column name (without the suffix) for the COL token
        col_name = col.replace("_left", "").replace("_used_cars","")  # Adjust suffixes as needed based on specific dataset names
        val = clean_text(row[col])
        left_parts.append(f"COL {col_name} VAL {val}")

    right_parts = []
    for col in right_cols:
        col_name = col.replace("_right", "").replace("_vehicles", "")  # Adjust suffixes as needed
        val = clean_text(row[col])
        right_parts.append(f"COL {col_name} VAL {val}")

    left_str = " ".join(left_parts)
    right_str = " ".join(right_parts)
    label = str(int(row[label_col]))
    if len(left_parts) > 0 and len(right_parts) > 0 and len(left_parts) == len(right_parts):
        # If the same number of columns on both sides, we can optionally align them
        # by interleaving COL and VAL tokens. For simplicity, we keep them separate here.
        return f"{left_str}\t{right_str}\t{label}"
    else:
        raise ValueError(f"Row has mismatched columns: {len(left_parts)} left vs {len(right_parts)} right. Row data: {row.to_dict()}")



def convert_csv_to_ditto(input_path, output, train_ratio=0.7, val_ratio=0.15):

    df = pd.read_csv(input_path)

    # Identify label column (usually 'match', 'label', or similar)
    if 'match_label' in df.columns:
        label_col = 'match_label'
    else:
        raise ValueError("Could not find a label column (e.g., 'match', 'gold').")

    cols = [c for c in df.columns if c != label_col and c != 'Unnamed: 0']

    suffix_a = "_used_cars"
    suffix_b = "_vehicles"

    left_cols = [c for c in cols if c.endswith(suffix_a) and "vin" not in c]  # Exclude VIN columns if they exist
    right_cols = [c for c in cols if c.endswith(suffix_b) and "vin" not in c]

    print(f"Detected left columns ({suffix_a}): {left_cols}")
    print(f"Detected right columns ({suffix_b}): {right_cols}")

    # Process all rows
    ditto_lines = df.apply(lambda row: row_to_ditto_string(row, left_cols, right_cols, label_col), axis=1).tolist()

    #create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        for line in ditto_lines:
            f.write(line + "\n")

def main():
    # Adjust paths as necessary
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="pairs.csv", help="Input CSV file with pairs")
    parser.add_argument("-o", "--output", type=str, default="ditto/data/used_cars_vehicles/data.txt", help="Output directory for Ditto formatted files")
    args = parser.parse_args()

    input_csv = args.input
    output = args.output

    if os.path.exists(input_csv):
        convert_csv_to_ditto(input_csv, output)
    else:
        print(f"File {input_csv} not found. Please check the path.")


if __name__ == "__main__":
    main()
