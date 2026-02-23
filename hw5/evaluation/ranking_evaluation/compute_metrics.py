import math
from typing import List, Optional, Dict
import os
import json
import argparse
import csv


def load_annotations(annotations_path: str) -> Dict[str, List[int]]:
    """Return a map: query_id -> list of relevances in rank order (1/0)."""
    by_query = {}
    if not os.path.exists(annotations_path):
        return by_query
    with open(annotations_path, "r", encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            qid = a.get("query_id") or a.get("id") or a.get("query")
            rank = int(a.get("rank", 0))
            by_query.setdefault(qid, []).append((rank, int(a["relevance"])))
    sorted_by_query = {}
    for qid, items in by_query.items():
        items.sort(key=lambda x: x[0])
        sorted_by_query[qid] = [rel for _, rel in items]
    return sorted_by_query

def precision_at_k(rels: List[int], k: int) -> float:
    if len(rels) == 0:
        return 0.0
    k = min(k, len(rels))
    return sum(rels[:k]) / k

def average_precision(rels: List[int]) -> float:
    num_rel = sum(rels)
    if num_rel == 0:
        return 0.0
    score = 0.0
    rel_seen = 0
    for i, r in enumerate(rels, start=1):
        if r:
            rel_seen += 1
            score += rel_seen / i
    return score / num_rel

def dcg(rels: List[int], k: int) -> float:
    score = 0.0
    for i in range(min(k, len(rels))):
        gain = (2 ** rels[i] - 1)
        score += gain / math.log2(i + 2)
    return score

def ndcg_at_k(rels: List[int], k: int) -> float:
    actual = dcg(rels, k)
    ideal = dcg(sorted(rels, reverse=True), k)
    return actual / ideal if ideal > 0 else 0.0

def compute_metrics(k: int = 10, annotations_path: Optional[str] = None):
    if annotations_path is None:
        print("No annotations file specified for metrics.")
        return
    ann = load_annotations(annotations_path)
    print(f"{ann}")
    precisions = []
    aps = []
    ndcgs = []
    for qid, rels in ann.items():
        print(f"Metrics for query_id={qid} with relevances={rels}")
        precision = precision_at_k(rels, k)
        ap = average_precision(rels)
        ndcg = ndcg_at_k(rels, k)
        print(f"  Precision@{k}: {precision:.4f}")
        print(f"  Average Precision: {ap:.4f}")
        print(f"  nDCG@{k}: {ndcg:.4f}")
        precisions.append(precision_at_k(rels, k))
        aps.append(average_precision(rels))
        ndcgs.append(ndcg_at_k(rels, k))
    if not precisions:
        print("No annotations found.")
        return
    print(f"Precision@{k}: {sum(precisions)/len(precisions):.4f}")
    print(f"MAP: {sum(aps)/len(aps):.4f}")
    print(f"nDCG@{k}: {sum(ndcgs)/len(ndcgs):.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute ranking evaluation metrics (Precision@K, MAP, nDCG@K) based on relevance annotations.")
    parser.add_argument("annotations_path", type=str, help="Path to the JSONL file containing relevance annotations for queries.")
    parser.add_argument("--k", type=int, default=10, help="The rank cutoff for Precision@K and nDCG@K")
    args = parser.parse_args()
    compute_metrics(k=args.k, annotations_path=args.annotations_path)