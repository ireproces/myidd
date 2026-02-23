import argparse
import pandas as pd
import json
import re
import os


def clean_text(text):
    text = str(text)
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Simple cleaning to allow more characters than strict alphanumeric but remove layout control
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def row_to_json_pair(row, left_cols, right_cols, label_col):
    """
    Converts a single row into a JSON structure:
    [
      {"col1": "val1", ...},
      {"col1": "val1", ...}
    ]
    It also optionally handles the label if needed, but standard input_small format
    usually just contains the features for prediction.
    """
    left_obj = {}
    for col in left_cols:
        # Extract the original column name (strip suffix)
        col_name = col.replace("_left", "").replace("_used_cars", "")
        val = clean_text(row[col])
        left_obj[col_name] = val

    right_obj = {}
    for col in right_cols:
        col_name = col.replace("_right", "").replace("_vehicles", "")
        val = clean_text(row[col])
        right_obj[col_name] = val

    # The format in the example seems to include the label or just the pair.
    # Based on input_small.json examples, it is often a list of two dictionaries.
    # If a label is required by the downstream task, it might be separate,
    # but strictly following the [left_obj, right_obj] structure:
    return [left_obj, right_obj]


def convert_csv_to_jsonl(input_path, output_path):
    df = pd.read_csv(input_path)

    # Determine label column if present (though JSONL input for prediction might not strictly need it inside the object)
    label_col = 'match_label' if 'match_label' in df.columns else None

    # Exclude unnecessary columns
    exclude = ['Unnamed: 0', 'id', label_col]
    cols = [c for c in df.columns if c not in exclude]

    # Dynamic detection of suffixes based on dataset
    suffix_a = "_left"
    suffix_b = "_right"

    # Fallback for specific used_cars dataset if standard suffixes aren't found
    if not any(c.endswith(suffix_a) for c in cols):
        suffix_a = "_used_cars"
        suffix_b = "_vehicles"

    left_cols = [c for c in cols if c.endswith(suffix_a) and "vin" not in c]
    right_cols = [c for c in cols if c.endswith(suffix_b) and "vin" not in c]

    print(f"Detected left columns ({suffix_a}): {left_cols}")
    print(f"Detected right columns ({suffix_b}): {right_cols}")

    json_lines = df.apply(lambda row: row_to_json_pair(row, left_cols, right_cols, label_col), axis=1).tolist()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in json_lines:
            f.write(json.dumps(item) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="pairs.csv", help="Input CSV file with pairs")
    parser.add_argument("-o", "--output", type=str, default="ditto/data/input_small.json", help="Output JSONL file")
    args = parser.parse_args()

    input_csv = args.input
    output_path = args.output

    if os.path.exists(input_csv):
        convert_csv_to_jsonl(input_csv, output_path)
    else:
        print(f"File {input_csv} not found.")


if __name__ == "__main__":
    main()
