import pandas as pd
import json
from tqdm import tqdm

# Estimate total lines for progress bar (optional, improves tqdm)
def get_num_lines(filename):
    with open(filename) as f:
        lines_amount = 0
        while f.readline() != "":
            lines_amount +=1
        return lines_amount

def process(schema_file: str, source_dataset: str, target_dataset:str, chunk_size: int = 1000, threshold: float = 0.5, row_id_start: int = 0):
    first_chunk = True

    # Load schema mapping once
    with open(schema_file, "r") as f:
        schema = json.load(f)

    lines_amount = get_num_lines(source_dataset)
    seen_vins = set()  # To track seen VINs for deduplication
    for chunk in tqdm(pd.read_csv(source_dataset, chunksize=chunk_size), total=lines_amount // chunk_size + 1, desc=f"Processing {source_dataset}"):
        chunk = chunk[[c for c in chunk.columns if c in schema.keys()]]
        chunk = chunk.rename(columns=schema)
        # Replace empty strings and whitespace with NaN
        chunk = chunk.replace(r'^\s*$', pd.NA, regex=True)
        min_non_na = int(len(chunk.columns) * threshold)
        chunk = chunk.dropna(thresh=min_non_na)
        chunk = chunk.reset_index(drop=True)
        chunk["row_id"] = chunk.index + row_id_start
        row_id_start += len(chunk)
        # Deduplicate based on VIN
        if "vin" in chunk.columns:
            chunk = chunk[~chunk["vin"].isin(seen_vins)]
            seen_vins.update(chunk["vin"].dropna().unique())
        chunk.to_csv(target_dataset, mode="a", index=False, header=first_chunk)
        first_chunk = False
    return row_id_start

if __name__ == "__main__":
    row_id_start = 0
    row_id_start = process("used_cars_to_schema.json", "used_cars_data.csv", "a_used_cars_data.csv",1000, 0.7, row_id_start)
    
    process("vehicles_to_schema.json", "vehicles.csv", "a_vehicles.csv", 1000, 0.7, row_id_start)