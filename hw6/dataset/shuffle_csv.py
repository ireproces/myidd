import argparse
import pandas as pd

# shuffler script of csv file
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shuffle a CSV file")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("output_csv", help="Path to the output shuffled CSV file")
    args = parser.parse_args()
    print(f"Shuffling {args.input_csv} and saving to {args.output_csv}...")
    df = pd.read_csv(args.input_csv)
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    df_shuffled.to_csv(args.output_csv, index=False)