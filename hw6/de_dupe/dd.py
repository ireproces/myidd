import pandas as pd
import dedupe
import os
import logging
import argparse
import random
import re
import numpy as np

# Setup logging
logging.getLogger().setLevel(logging.WARNING)


def preprocess(column):
    """
    Clean data strings.
    """
    if pd.isna(column):
        return None
    column = str(column).strip().lower()
    if column == "":
        return None
    return column


def preprocess_price(column):
    """
    Clean price data to ensure it is a float or None.
    """
    if pd.isna(column):
        return None

    # Convert to string first to strip non-numeric characters if necessary
    s_col = str(column).strip().lower()
    if s_col == "":
        return None

    # Remove currency symbols or other non-numeric chars if present
    s_col = re.sub(r'[^\d\.]', '', s_col)

    try:
        return float(s_col)
    except ValueError:
        return None


def load_data(filename):
    """
    Read the pair-based CSV and split it into two dictionaries of records
    compatible with dedupe.RecordLink.
    """
    print(f"Loading data from {filename}...")
    df = pd.read_csv(filename)

    # Define suffixes
    suffix_a = "_used_cars"
    suffix_b = "_vehicles"

    records_1 = {}
    records_2 = {}

    # Ground truth storage for evaluation
    gold_standard = {}  # {(id_a, id_b): match_label}

    # Iterate over rows to reconstruct the entities
    for idx, row in df.iterrows():
        # Construct ID strings
        id_a = f"a_{idx}"
        id_b = f"b_{idx}"

        # Extract Dictionary for Left Record
        rec_a = {
            "manufacturer": preprocess(row.get(f"manufacturer{suffix_a}")),
            "model": preprocess(row.get(f"model{suffix_a}")),
            "year": preprocess(row.get(f"year{suffix_a}")),
            "price": preprocess_price(row.get(f"price{suffix_a}")),  # Use numeric preprocessor
            "fuel_type": preprocess(row.get(f"fuel_type{suffix_a}")),
            "color": preprocess(row.get(f"color{suffix_a}")),
            "body_type": preprocess(row.get(f"body_type{suffix_a}"))
        }

        # Extract Dictionary for Right Record
        rec_b = {
            "manufacturer": preprocess(row.get(f"manufacturer{suffix_b}")),
            "model": preprocess(row.get(f"model{suffix_b}")),
            "year": preprocess(row.get(f"year{suffix_b}")),
            "price": preprocess_price(row.get(f"price{suffix_b}")),  # Use numeric preprocessor
            "fuel_type": preprocess(row.get(f"fuel_type{suffix_b}")),
            "color": preprocess(row.get(f"color{suffix_b}")),
            "body_type": preprocess(row.get(f"body_type{suffix_b}"))
        }

        records_1[id_a] = rec_a
        records_2[id_b] = rec_b

        # Store Truth
        label = row.get("match_label")
        if label is not None:
            gold_standard[(id_a, id_b)] = int(label)

    return records_1, records_2, gold_standard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input blocked csv file (e.g., blocked1_test.csv)")
    parser.add_argument("--settings", default="dedupe_learned_settings", help="Path to settings file")
    parser.add_argument("--training", default="dedupe_training.json", help="Path to training file")
    parser.add_argument("--train_fraction", type=float, default=0.3, help="Fraction of data to use for training")
    args = parser.parse_args()

    input_file = args.input_file
    settings_file = args.settings
    training_file = args.training

    # 1. Ingest Data
    data_1, data_2, ground_truth = load_data(input_file)

    # Define Fields for Dedupe (Updated for Dedupe 3.0+)
    fields = [
        dedupe.variables.String('manufacturer'),
        dedupe.variables.String('model'),
        dedupe.variables.Exact('year', has_missing=True),
        dedupe.variables.Price('price', has_missing=True),
        dedupe.variables.ShortString('fuel_type', has_missing=True),
        dedupe.variables.ShortString('color', has_missing=True),
        dedupe.variables.ShortString('body_type', has_missing=True),
    ]

    linker = dedupe.RecordLink(fields)

    # 2. Training / Loading Settings
    if os.path.exists(settings_file):
        print(f"Reading from {settings_file}")
        with open(settings_file, 'rb') as f:
            linker = dedupe.StaticRecordLink(f)
    else:
        print("Training dedupe model...")

        # Prepare training data programmatically using ground truth match_labels
        match_keys = [pair for pair, lbl in ground_truth.items() if lbl == 1]
        distinct_keys = [pair for pair, lbl in ground_truth.items() if lbl == 0]

        # Subsample for training
        random.seed(42)
        n_train = int(len(ground_truth) * args.train_fraction)

        labeled_examples = {
            "match": [],
            "distinct": []
        }

        if match_keys:
            # Only take a subset for training, keep the rest for test if needed, though we evaluate on all input
            sample_m = random.sample(match_keys, min(len(match_keys), n_train // 2 + 1))
            labeled_examples["match"] = [(data_1[u], data_2[v]) for u, v in sample_m]

        if distinct_keys:
            sample_d = random.sample(distinct_keys, min(len(distinct_keys), n_train // 2 + 1))
            labeled_examples["distinct"] = [(data_1[u], data_2[v]) for u, v in sample_d]

        print(
            f"Training with {len(labeled_examples['match'])} matches and {len(labeled_examples['distinct'])} non-matches.")

        linker.prepare_training(data_1, data_2, training_file=training_file if os.path.exists(training_file) else None)
        linker.mark_pairs(labeled_examples)
        linker.train()

        with open(settings_file, 'wb') as sf:
            linker.write_settings(sf)

    # 3. Clustering / Matching
    print("Classifying pairs...")

    candidate_pairs = list(ground_truth.keys())

    # Construct input for comparison
    pair_records = []
    for id_a, id_b in candidate_pairs:
        pair_records.append((data_1[id_a], data_2[id_b]))

    # --- FIX: Calculate scores manually using internal Dedupe methods ---
    # Dedupe doesn't expose a direct 'score_pairs' method for RecordLink easily in the public API.
    # We must calculate distances using the Data Model and then predict using the Classifier.

    # 1. Compute distances for the pairs
    descriptions = linker.data_model.distances(pair_records)

    # 2. Compute probabilities using the logistic regression classifier
    # predict_proba returns an array of shape (n_samples, 2), we want the probability of class 1.
    scores = linker.classifier.predict_proba(descriptions)[:, 1]

    # 4. Evaluate
    threshold = 0.5
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    print("Evaluating results...")

    for idx, score in enumerate(scores):
        id_a, id_b = candidate_pairs[idx]
        actual = ground_truth[(id_a, id_b)]
        predicted = 1 if score > threshold else 0

        if predicted == 1 and actual == 1:
            tp += 1
        elif predicted == 1 and actual == 0:
            fp += 1
        elif predicted == 0 and actual == 0:
            tn += 1
        elif predicted == 0 and actual == 1:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"--- Evaluation (Threshold: {threshold}) ---")
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TN: {tn}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")


if __name__ == "__main__":
    main()
