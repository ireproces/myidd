tp = int(input("insert tp:"))
fp = int(input("insert fp:"))
fn = int(input("insert fn:"))
tn = int(input("insert tn:"))

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
print("Precision: ", precision)
print("Recall: ", recall)
print("F1 Score: ", f1_score)