
import random
import os
import argparse
import pandas as pd


def split_dataset(input_path, output_dir, train_ratio=0.7, valid_ratio=0.15, seed=42):
    random.seed(seed)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = pd.read_csv(input_path)

    # Split
    total_size = len(df)
    indices = list(range(total_size))
    random.shuffle(indices)

    train_end = int(train_ratio * total_size)
    valid_end = train_end + int(valid_ratio * total_size)
    train_indices = indices[:train_end]
    valid_indices = indices[train_end:valid_end]
    test_indices = indices[valid_end:]

    train_data = df.iloc[train_indices]
    valid_data = df.iloc[valid_indices]
    test_data = df.iloc[test_indices]

    # Save splits
    train_data.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    valid_data.to_csv(os.path.join(output_dir, "valid.csv"), index=False)
    test_data.to_csv(os.path.join(output_dir, "test.csv"), index=False)

    print(f"Split completed: Train={len(train_data)}, Valid={len(valid_data)}, Test={len(test_data)}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input file path (e.g., data.txt)")
    parser.add_argument("output_dir", type=str, help="Output directory for train/valid/test splits")
    args = parser.parse_args()

    split_dataset(args.input, args.output_dir)
