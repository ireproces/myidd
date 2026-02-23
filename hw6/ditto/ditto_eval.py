# Will iterate through JSON lines, will use the row_id to see if the pair is in match or not, will see what the verdict of ditto is and will
# write out in true.csv and false.csv the correct predictions and the wrong prections

import pandas as pd
import json
import argparse

from scipy.constants import precision


def row_id_pair_is_contained_in_match_table(left_id, right_id, match_table):
    # Check if the pair (left_id, right_id) is in the match table with a match_label of 1
    try:
        left_id = int(float(left_id))  # Convert to int if it's a float string
        right_id = int(float(right_id))
        match_row = match_table[(match_table['row_id_used_cars'] == left_id) & (match_table['row_id_vehicles'] == right_id)]
        if not match_row.empty:
            return True
        return False
    except Exception as e:
        print(f"Error checking pair ({left_id}, {right_id}): {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="ditto/data/input_small.json", help="Input JSONL file with pairs")
    parser.add_argument("-p", "--predictions", type=str, default="ditto/data/output_small.jsonl", help="JSONL file with Ditto predictions")
    parser.add_argument("-m", "--match_table", type=str, default="match_table.csv", help="CSV file containing the match table with row_id and match_label")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        input_data = [json.loads(line) for line in f]
    with open(args.predictions, 'r', encoding='utf-8') as f:
        predictions = [json.loads(line) for line in f]
    match_table = pd.read_csv(args.match_table)

    TP=0
    FP=0
    TN=0
    FN=0
    for input_pair, pred in zip(input_data, predictions):
        left_obj, right_obj = input_pair
        pred_label = pred.get('match')
        true_label = 1 if row_id_pair_is_contained_in_match_table(left_obj['row_id'], right_obj['row_id'], match_table) else 0
        #print(f"Left ID: {left_obj['row_id']}, Right ID: {right_obj['row_id']}, True Label: {true_label}, Predicted Label: {pred_label}")
        if pred_label == 1 and true_label == 1:
            TP += 1
        elif pred_label == 1 and true_label == 0:
            FP += 1
        elif pred_label == 0 and true_label == 0:
            TN += 1
        elif pred_label == 0 and true_label == 1:
            FN += 1

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1 Score: ", f1_score)
    print("TP: ", TP)
    print("FP: ", FP)
    print("FN: ", FN)
    print("TN: ", TN)


if __name__ == "__main__":
    main()

