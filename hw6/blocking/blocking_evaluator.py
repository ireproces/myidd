import pandas as pd
import argparse
# we have excluded_pairs.csv e blocked_pairs.csv.
# if match label is 1 in blocked_pairs.csv we have a true positive, if match label is 0 we have a false positive.
# if match label is 1 in excluded_pairs.csv we have a false negative, if match label is 0 we have a true negative.



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--blocked", type=str, default="blocked_pairs.csv", help="CSV file containing the blocked pairs with match labels")
    parser.add_argument("-e", "--excluded", type=str, default="excluded_pairs.csv", help="CSV file containing the excluded pairs with match labels")
    args = parser.parse_args()

    blocked_df = pd.read_csv(args.blocked)
    excluded_df = pd.read_csv(args.excluded)

    TP = len(blocked_df[blocked_df['match_label'] == 1])
    FP = len(blocked_df[blocked_df['match_label'] == 0])
    FN = len(excluded_df[excluded_df['match_label'] == 1])
    TN = len(excluded_df[excluded_df['match_label'] == 0])

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