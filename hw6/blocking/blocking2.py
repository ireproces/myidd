import jellyfish
import argparse
import os
import pandas as pd
import hashlib

WORKING_DIR = "blocks2"
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


def get_typo_tolerant_keys(row) -> set:
    keys = set()

    brand = str(row.get('manufacturer', '')).lower().strip()
    model = str(row.get('model', '')).lower().strip()
    year = str(row.get('year', '')).strip()

    # 1. Brand+Model soundex
    if brand and model:
        brand_key = jellyfish.soundex(brand)
        model_key = jellyfish.soundex(model)
        key1 = f"{brand_key}_{model_key}"
        keys.add(key1)

    # 2. Brand + first char of Model
    if brand and model:
        key2 = f"{brand}_{model[0]}"
        keys.add(key2)

    # 3. Model only 
    if model:
        keys.add(model)

    # 4. Year (if present and valid) used as a loose block key
    # Note: Blocking purely on Year might create huge blocks, but 
    # combined with other methods in a multi-pass approach it improves recall.
    # For this specific file structure, let's keep it specific to avoid explosion.
    if year.isdigit() and len(year) == 4:
        keys.add(f"year_{year}")

    # Hash keys for safe filenames
    hashed_keys = {hashlib.md5(k.encode()).hexdigest() for k in keys}
    return hashed_keys


def handle_row(row):
    # Split row into two entities
    first_row_data = {col: row[f"{col}_used_cars"] for col in COLUMN_NAMES if f"{col}_used_cars" in row}
    second_row_data = {col: row[f"{col}_vehicles"] for col in COLUMN_NAMES if f"{col}_vehicles" in row}

    first_row = pd.Series(first_row_data)
    second_row = pd.Series(second_row_data)

    keys1 = get_typo_tolerant_keys(first_row)
    keys2 = get_typo_tolerant_keys(second_row)

    # Find intersection: if they match on AT LEAST one key strategy
    common_keys = keys1.intersection(keys2)
    #print("Processed row with keys: ", keys1, " vs ", keys2, " => Common keys: ", common_keys)
    if common_keys:
        return row, common_keys
    return None, None


def main():
    init()
    parser = argparse.ArgumentParser(description="Create blocks for high recall based on multiple typo-tolerant keys.")
    parser.add_argument("table1", help="Path to the first aligned CSV file")
    parser.add_argument("-o", "--output", help="Path to the output csv file", default="blocked_pairs.csv")
    parser.add_argument("-e", "--excluded", help="Path to a CSV file with the excluded rows", default="excluded_rows.csv")
    args = parser.parse_args()


    # Process table
    for chunk in pd.read_csv(args.table1, chunksize=100000):
        for index, row in chunk.iterrows():
            processed_row, matching_keys = handle_row(row)

            if processed_row is not None:
                # Write to ALL matching blocks (OR logic means if it matches key A OR key B, it goes in both blocks)
                processed_row.to_frame().T.to_csv(args.output, mode='a', index=False, header=not os.path.exists(args.output))
            else:
                row.to_frame().T.to_csv(args.excluded, mode='a', index=False, header=not os.path.exists(args.excluded))


if __name__ == "__main__":
    main()
