import recordlinkage
import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="input file")
args = parser.parse_args()

# 1. Load the blocked pairs
input_file = args.input  # Ensure this path matches your file location
print(f"Loading {input_file}...")
df_pairs = pd.read_csv(input_file)

# --- SAVE GROUND TRUTH ---
# We preserve the match_label to evaluate later.
# The index of actual_matches corresponds to the row index of df_pairs.
actual_labels = df_pairs["match_label"].values

# 2. Separate the pairs back into two DataFrames
suffix_a = "_used_cars"
suffix_b = "_vehicles"

# Columns explicitly excluded from feature comparison (cheating or metadata)
columns_to_drop_a = [f"vin{suffix_a}", "match_label", f"row_id{suffix_a}"]
columns_to_drop_b = [f"vin{suffix_b}", "match_label", f"row_id{suffix_b}"]

# Filter columns present in the file
cols_a = [c for c in df_pairs.columns if c.endswith(suffix_a)]
cols_b = [c for c in df_pairs.columns if c.endswith(suffix_b)]

dfA = df_pairs[cols_a].copy()
dfB = df_pairs[cols_b].copy()

# 3. Clean up DataFrames
# Drop specific columns if they exist in the split frames
for col in columns_to_drop_a:
    if col in dfA.columns: dfA.drop(columns=[col], inplace=True)
for col in columns_to_drop_b:
    if col in dfB.columns: dfB.drop(columns=[col], inplace=True)

# Normalize column names
dfA.columns = [c.replace(suffix_a, "") for c in dfA.columns]
dfB.columns = [c.replace(suffix_b, "") for c in dfB.columns]

# Ensure unique numeric indices for alignment
dfA.index.name = "id_a"
dfB.index.name = "id_b"

# 4. Construct the Candidate Links
# Since row i in input is a pair, we link row i of dfA to row i of dfB
candidate_links = pd.MultiIndex.from_arrays(
    [dfA.index, dfB.index],
    names=["id_a", "id_b"]
)

# 5. Define Comparison Logic
compare_cl = recordlinkage.Compare()

compare_cl.exact("year", "year", label="year")
compare_cl.string("body_type", "body_type", method="jarowinkler", threshold=0.6, label="body_type")
compare_cl.string("fuel_type", "fuel_type", method="jarowinkler", threshold=0.6, label="fuel_type")
compare_cl.string("manufacturer", "manufacturer", method="jarowinkler", threshold=0.6, label="manufacturer")
compare_cl.string("model", "model", method="jarowinkler", threshold=0.6, label="model")
compare_cl.string("color", "color", method="jarowinkler", threshold=0.6, label="color")
compare_cl.string("description", "description", method="jarowinkler", threshold=0.60, label="description")
compare_cl.numeric("price", "price", method="gauss", offset=100.0, scale=1000.0, label="price")
compare_cl.numeric("mileage", "mileage", method="gauss", offset=500.0, scale=5000.0, label="mileage")

# 6. Compute Features
print("Computing similarity features...")
features = compare_cl.compute(candidate_links, dfA, dfB)

# 7. Classification
# Simple weighted sum or threshold.
# 'features.sum(axis=1)' gives a score between 0 and N_features
score = features.sum(axis=1)

# Threshold for being considered a "Match"
THRESHOLD = 5.0
predicted_labels = (score >= THRESHOLD).astype(int)

# 8. Evaluation
print(f"\n--- Evaluation (Threshold: {THRESHOLD}) ---")

# We align predictions with actuals.
# Since we used diagonal indexing (0-0, 1-1), the array order matches.
# predicted_labels is a Series indexed by MultiIndex. We extract values.
pred_array = predicted_labels.values

# Confusion Matrix Elements
# TP: Pred=1, Actual=1
# FP: Pred=1, Actual=0
# TN: Pred=0, Actual=0
# FN: Pred=0, Actual=1

tp = np.sum((pred_array == 1) & (actual_labels == 1))
fp = np.sum((pred_array == 1) & (actual_labels == 0))
tn = np.sum((pred_array == 0) & (actual_labels == 0))
fn = np.sum((pred_array == 0) & (actual_labels == 1))

print(f"TP: {tp}")
print(f"FP: {fp}")
print(f"FN: {fn}")
print(f"TN: {tn}")

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
