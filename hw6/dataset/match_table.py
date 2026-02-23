import pandas as pd
import argparse
import os
import concurrent.futures
import time

def worker(chunk_used_cars, chunk_vehicles, output_file, process_id):
    start_time = time.time()
    print(f"Process {process_id} started...")
    match_chunk(chunk_used_cars, chunk_vehicles, output_file)
    end_time = time.time()
    print(f"Process {process_id} completed in {end_time - start_time:.2f} seconds.")

def match_chunk(chunk_used_cars, chunk_vehicles, output_file):
    merged = pd.merge(chunk_used_cars, chunk_vehicles, on="vin", how="inner", suffixes=('_used_cars', '_vehicles'))
    if not merged.empty:
        merged[["row_id_used_cars", "row_id_vehicles"]].to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a match table based on VIN from two aligned datasets.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    parser.add_argument("table2", help="Path to the second aligned CSV file (e.g., aligned_vehicles.csv)")
    parser.add_argument("-o", "--output", help="Path to the output match table CSV file (default: match_table.csv)", default="match_table.csv")
    args = parser.parse_args()

    # Remove output file if it exists to avoid header issues
    if os.path.exists(args.output):
        os.remove(args.output)

    max_workers = os.cpu_count() or 1
    #print(f"Using {max_workers} parallel workers for matching.")

    process_id = 0
    for chunk_used_cars in pd.read_csv(args.table1, chunksize=100000):
        for chunk_vehicles in pd.read_csv(args.table2, chunksize=100000):
            worker(chunk_used_cars, chunk_vehicles, args.output, process_id)
            process_id += 1