# Column CSV dropper

import pandas as pd
import argparse

def drop_columns(input_file, output_file, columns_to_drop):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Drop the specified columns
    df_dropped = df.drop(columns=columns_to_drop)

    # Save the modified DataFrame to a new CSV file
    df_dropped.to_csv(output_file, index=False)
    print(f"Columns {columns_to_drop} dropped and saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Drop specified columns from a CSV file.")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("output_file", help="Path to output CSV file")
    parser.add_argument("-c", "--columns", nargs='+', required=True, help="List of columns to drop")

    args = parser.parse_args()

    drop_columns(args.input_file, args.output_file, args.columns)

if __name__ == "__main__":
    main()