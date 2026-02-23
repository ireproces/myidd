import jellyfish
import argparse
import os
import pandas as pd
import hashlib

WORKING_DIR = "blocks1"
COLUMN_NAMES = []
SUFFIXES = []


def init():
    with open("schema.txt", "r") as f:
        with open("suffixes.txt", "r") as suffix_file:
            for line in f:
                column_name = line.strip()
                COLUMN_NAMES.append(column_name)
            for line in suffix_file:
                suffix = line.strip()
                SUFFIXES.append(suffix)


def get_typo_tolerant_keys(row) -> str:
    brand = str(row.get('manufacturer', '')).lower().strip()
    model = str(row.get('model', '')).lower().strip()
    brand_key = jellyfish.soundex(brand)
    model_key = jellyfish.soundex(model)
    key_string = f"{brand_key}_{model_key}"
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def handle_row(row):
    # row is now a pandas Series, so we can access keys directly with brackets
    # Create clean series for each entity based on the schema
    first_row_data = {col: row[f"{col}_used_cars"] for col in COLUMN_NAMES if f"{col}_used_cars" in row}
    second_row_data = {col: row[f"{col}_vehicles"] for col in COLUMN_NAMES if f"{col}_vehicles" in row}

    first_row = pd.Series(first_row_data)
    second_row = pd.Series(second_row_data)

    first_key = get_typo_tolerant_keys(first_row)
    second_key = get_typo_tolerant_keys(second_row)
    #print(f"Processed row with keys: {first_key} (used_cars) vs {second_key} (vehicles)")
    if first_key == second_key:
        return row, first_key  # Return the key as well for file naming
    return row, None


def main():
    init()
    parser = argparse.ArgumentParser(description="Create blocks based on typo-tolerant keys.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    parser.add_argument("-o", "--output", help="Path to the output csv file", default="blocked_pairs.csv")
    parser.add_argument("-e", "--excluded", help="Path to a CSV file with the excluded rows", default="excluded_rows.csv")
    args = parser.parse_args()

    # Process first table
    for chunk in pd.read_csv(args.table1, chunksize=100000):
        # Using iterrows allows access by string keys, handling spaces correctly
        for index, row in chunk.iterrows():
            processed_row, key = handle_row(row)
            if key is not None:
                # Append to the file for that specific block
                processed_row.to_frame().T.to_csv(args.output, mode='a', index=False,
                                                  header=not os.path.exists(args.output))
            else:
                processed_row.to_frame().T.to_csv(args.excluded, mode='a', index=False,
                                                  header=not os.path.exists(args.excluded))


if __name__ == "__main__":
    main()
