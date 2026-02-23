import argparse
import pandas as pd
import random
import os

# We will create the pairs to be saved in a CSV with a new column for their match label
# It will be balanced, using all the positives matches in the match_table and getting the same amount of random negative matches by randomly picking and checking that it's not present in the match_table

def match_chunk(chunk_a, chunk_b):
    # Ensure indices are reset to avoid merge issues if chunks came from specific weird indexing
    chunk_a = chunk_a.reset_index(drop=True)
    chunk_b = chunk_b.reset_index(drop=True)

    # Merge on VIN to find positive matches (assuming VIN is the join key)
    merged = pd.merge(chunk_a, chunk_b, on="vin", how="inner", suffixes=('_used_cars', '_vehicles'))

    if not merged.empty:
        merged["match_label"] = 1
        # Create explicit columns for both VINs to match negative pair schema later
        merged["vin_used_cars"] = merged["vin"]
        merged["vin_vehicles"] = merged["vin"]

        # Drop the common key because we now have specific suffixed keys
        merged = merged.drop(columns=["vin"])
    return merged


def create_negative_pairs(dataset1_path, dataset2_path, num_pairs):
    # Get total lines to know range for random sampling (subtract 1 for header)
    n_rows1 = sum(1 for _ in open(dataset1_path)) - 1
    n_rows2 = sum(1 for _ in open(dataset2_path)) - 1

    # Generate random indices
    if num_pairs > n_rows1: num_pairs = n_rows1
    if num_pairs > n_rows2: num_pairs = n_rows2

    indices1 = sorted(random.sample(range(n_rows1), num_pairs))
    indices2 = sorted(random.sample(range(n_rows2), num_pairs))

    def load_rows_by_indices(path, indices):
        target_indices = set(indices)
        return pd.read_csv(path, skiprows=lambda x: x > 0 and (x - 1) not in target_indices)

    print("Loading random rows from dataset 1...")
    df1 = load_rows_by_indices(dataset1_path, indices1)

    print("Loading random rows from dataset 2...")
    df2 = load_rows_by_indices(dataset2_path, indices2)

    # Shuffle to decouple the sorted loading order so we get random pairings
    df1 = df1.sample(frac=1).reset_index(drop=True)
    df2 = df2.sample(frac=1).reset_index(drop=True)

    # Rename ALL columns including VIN
    df1_renamed = df1.rename(columns={c: f"{c}_used_cars" for c in df1.columns})
    df2_renamed = df2.rename(columns={c: f"{c}_vehicles" for c in df2.columns})

    # Concatenate side-by-side.
    candidates = pd.concat([df1_renamed, df2_renamed], axis=1)

    # Filter out accidental positive matches (same VIN)
    candidates = candidates[candidates['vin_used_cars'] != candidates['vin_vehicles']]

    candidates['match_label'] = 0

    print(f"Created {len(candidates)} negative pairs")
    return candidates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create pairs of records for matching")
    parser.add_argument("-o", "--output", type=str, default="pairs.csv", help="Output CSV file for pairs")
    parser.add_argument("match_table", type=str, help="CSV file containing the match table")
    parser.add_argument("dataset1", type=str, help="First dataset CSV file")
    parser.add_argument("dataset2", type=str, help="Second dataset CSV file")
    args = parser.parse_args()

    if os.path.exists(args.output):
        os.remove(args.output)

    pos_count = 0
    header_written = False

    match_table_df = pd.read_csv(args.match_table)
    target_negative_count = len(match_table_df)

    # Run the positive pair extraction
    for chunk_used_cars in pd.read_csv(args.dataset1, chunksize=50000):
        for chunk_vehicles in pd.read_csv(args.dataset2, chunksize=50000):
            positive_pairs = match_chunk(chunk_used_cars, chunk_vehicles)

            if not positive_pairs.empty:
                pos_count += len(positive_pairs)
                # Write to CSV
                positive_pairs.to_csv(args.output, mode='a', index=False, header=not os.path.exists(args.output))

    print(f"Written positive pairs. Proceeding to create {target_negative_count} negative pairs...")

    # 2. Process Negative Pairs
    negative_pairs_df = create_negative_pairs(args.dataset1, args.dataset2, target_negative_count)

    if os.path.exists(args.output):
        # FIX: Align columns with existing file!
        # Read the header of the existing file to know the exact order
        try:
             existing_columns = pd.read_csv(args.output, nrows=0).columns.tolist()
             # Reorder negative_pairs_df to match existing schema exactly
             # This ensures 'match_label' and 'VIN' columns fall into the correct positions
             negative_pairs_df = negative_pairs_df[existing_columns]
        except pd.errors.EmptyDataError:
             # If file was created but empty (no positive pairs found), we leave order as is
             pass

    # Append negative pairs to the same output file
    negative_pairs_df.to_csv(args.output, mode='a', index=False, header=not os.path.exists(args.output))
