import pandas as pd
import argparse


def clean(df):
    df = df.dropna(subset=["row_id_used_cars", "row_id_vehicles"]).copy()
    df["row_id_used_cars"] = df["row_id_used_cars"].apply(lambda x: int(float(x)))
    df["row_id_vehicles"] = df["row_id_vehicles"].apply(lambda x: int(float(x)))
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="data.txt", help="Input file path (e.g., data.txt)")
    parser.add_argument("-o", "--output", type=str, default="cleaned_data.csv", help="Output CSV file path")
    args = parser.parse_args()

    df = pd.read_csv(args.input)  # Assuming tab-separated values
    df = clean(df)
    df.to_csv(args.output, index=False)
    print(f"Cleaned data saved to {args.output}")


if __name__ == "__main__":
    main()