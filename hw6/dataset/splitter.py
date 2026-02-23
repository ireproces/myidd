import pandas as pd
import argparse

def split_dataset(input_csv, output_csv, fraction=0.05, random_state=42):
    first_chunk = True
    for chunk in pd.read_csv(input_csv, chunksize=1000):  # Read in chunks to handle large files
        sample = chunk.sample(frac=fraction, random_state=random_state)
        sample.to_csv(output_csv, mode="a", index=False, header=first_chunk)
        first_chunk = False
    print(f"Saved rows ({fraction*100}%) to {output_csv}")

if __name__ == "__main__":
    # Change filenames as needed
    parser = argparse.ArgumentParser(description="Split a CSV dataset into a smaller fraction.")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("output_csv", help="Path to the output CSV file")
    parser.add_argument("--fraction", type=float, default=0.05, help="Fraction of the dataset to sample (default: 0.05)")
    args = parser.parse_args()
    split_dataset(args.input_csv, args.output_csv, args.fraction)