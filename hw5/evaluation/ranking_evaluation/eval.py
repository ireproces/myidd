import argparse
import json
import sys
import time
from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional
import math
import os
import ext_llm
from datetime import datetime
import webbrowser

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
DEFAULT_QUERIES_PATH = os.path.join(os.path.dirname(__file__), "queries.json")
FIELDS = {
    "research_papers": ["title", "authors", "summary", "link", "content"],
    "figures": ["figure_id", "caption", "paper_id","url", "image_url", "blob_data"],
    "tables": ["table_id", "caption", "paper_id", "data", "table_url", "blob_data"]
}
es = Elasticsearch(ES_HOST)


def make_default_annotations_path() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(os.path.dirname(__file__), f"annotations-{ts}.jsonl")

def run_queries(queries: List[Dict[str, Any]], top_k: int = 10, annotations_path: Optional[str] = None, human_mode: bool = False):
    if annotations_path is None:
        annotations_path = make_default_annotations_path()
    print(f"Annotations will be written to: {annotations_path}")

    scheduler = None
    if not human_mode:
        extllm = ext_llm.init(open("config.yaml", "r").read())
        llm_client = extllm.get_client("groq-llama")
        scheduler = extllm.get_scheduler(client=llm_client, retry_delay=10.0, initial_rate_limit=500, min_rate_limit=10, max_rate_limit=1000)
        scheduler.start()
    try:
        for q in queries:
            qid = q.get("id") or q.get("query_id") or q.get("query") or str(int(time.time()))
            index = q.get("index")
            query_param = {"multi_match": {"query": q.get("query"), "fields": FIELDS.get(index, ["title", "summary", "content"])}}

            print(f"\nQuery {qid} on index={index}: {q.get('query')}\n")
            res = es.search(index=index, query=query_param, size=top_k)
            hits = res.get("hits", {}).get("hits", [])
            print(f"hits={len(hits)}\n")
            # If human_mode, bypass LLM entirely and ask human per-hit
            if human_mode:
                for rank, h in enumerate(hits, start=1):
                    src = h.get("_source", {})
                    if index == "research_papers":
                        title = src.get("title") or src.get("caption") or src.get("paper_id") or h.get("_id")
                        summary = src.get("summary")
                        content = src.get("content") or ""
                        url = src.get("link")
                        print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Title: {title}\n  Summary: {summary}\n  Content: {content[:100]}...\n  URL: {url}\n")
                        prompt_url = url

                    elif index == "figures":
                        caption = src.get("caption")
                        image_url = src.get("image_url") or src.get("url")
                        paper_id = src.get("paper_id")
                        print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Image URL: {image_url}\n  Paper: {paper_id}\n")
                        prompt_url = image_url or paper_id

                    else:  # tables
                        caption = src.get("caption") or src.get("description")
                        data = src.get("data") or ""
                        table_url = src.get("table_url")
                        print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Table URL: {table_url}\n  Data snippet: {str(data)[:200]}\n")
                        prompt_url = table_url

                    try:
                        # automatically open the URL if it's a proper http(s) link
                        if prompt_url and isinstance(prompt_url, str) and prompt_url.startswith("http"):
                            try:
                                webbrowser.open_new_tab(prompt_url)
                            except Exception:
                                print(f"Failed to open URL in browser: {prompt_url}")
                        else:
                            print(f"No openable URL for this result: {prompt_url}")

                        raw = input(f"Enter relevance for rank {rank} id={h.get('_id')} [1/0] (provide 1 or 0): \nYour answer: ").strip()
                        if raw in ("0", "1"):
                            relevance = int(raw)
                        else:
                            print("Invalid input — defaulting to 0")
                            relevance = 0
                    except Exception:
                        print("Unable to read input — defaulting to 0")
                        relevance = 0

                    print(f"Annotation for rank {rank} id={h.get('_id')}: relevance={relevance}\n")
                    save_annotation({
                        "query_id": qid,
                        "index": index,
                        "result_id": h.get("_id"),
                        "rank": rank,
                        "relevance": relevance
                    }, annotations_path)
                # done with this query, continue
                continue

            # Non-human path: use LLM as before
            futures = []
            for rank, h in enumerate(hits, start=1):
                src = h.get("_source", {})
                if index == "research_papers":
                    title = src.get("title") or src.get("caption") or src.get("paper_id") or h.get("_id")
                    summary = src.get("summary")
                    content = src.get("content") or ""
                    url = src.get("link")
                    print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Title: {title}\n  Summary: {summary}\n  Content: {content[:100]}...\n  URL: {url}\n")
                    system_prompt = "You are an expert search result annotator. Given a query and a search result, determine if the result is relevant to the query. Respond with '1' if relevant and '0' if not relevant."
                    prompt = f"Query: {q.get('query')}\nTitle: {title}\nSummary: {summary}\nContent: {content}\nURL: {url}"
                    futures.append((rank, h, scheduler.submit_request(system_prompt, prompt)))

                elif index == "figures":
                    caption = src.get("caption")
                    image_url = src.get("image_url") or src.get("url")
                    paper_id = src.get("paper_id")
                    print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Image URL: {image_url}\n  Paper: {paper_id}\n")
                    system_prompt = "You are an expert annotator. Given a query, figure caption and image, decide if the figure answers the user's information need. Respond with '1' for relevant and '0' for not relevant."
                    prompt = f"Query: {q.get('query')}\nCaption: {caption}\nPaper: {paper_id}\nImageURL: {image_url}"
                    try:
                        if hasattr(scheduler, "submit_multimodal_request"):
                            future = scheduler.submit_multimodal_request(system_prompt, prompt, image=image_url)
                        else:
                            future = scheduler.submit_request(system_prompt, prompt + f"\n(IMAGE_URL: {image_url})")
                    except Exception:
                        future = scheduler.submit_request(system_prompt, prompt + f"\n(IMAGE_URL: {image_url})")
                    futures.append((rank, h, future))

                elif index == "tables":
                    caption = src.get("caption") or src.get("description")
                    data = src.get("data") or ""
                    table_url = src.get("table_url")
                    print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Table URL: {table_url}\n  Data snippet: {str(data)[:200]}\n")
                    system_prompt = "You are an expert annotator. Given a query and a table (caption and data), decide if the table is relevant to the query. Respond with '1' for relevant and '0' for not relevant."
                    prompt = f"Query: {q.get('query')}\nCaption: {caption}\nTableURL: {table_url}\nDataSnippet: {data}"
                    futures.append((rank, h, scheduler.submit_request(system_prompt, prompt)))

            for rank, h, future in futures:
                try:
                    relevance_str = scheduler.get_result(future).content.strip()
                    print("=" * 20)
                    print(f"LLM response for rank {rank} id={h.get('_id')}: '{relevance_str}'")
                    if "1" in relevance_str:
                        relevance = 1
                    elif "0" in relevance_str:
                        relevance = 0
                    else:
                        print(f"Unexpected LLM response for rank {rank} id={h.get('_id')}: '{relevance_str}'. Defaulting to relevance=0.")
                        relevance = 0
                except Exception as e:
                    print(f"Error getting relevance for rank {rank} id={h.get('_id')}: {e}")
                    relevance = 0

                # If human_mode enabled, allow human to confirm/override
                try:
                    raw = input(f"Enter relevance for rank {rank} id={h.get('_id')} [1/0] (Enter to accept LLM suggestion {relevance}, 's' to skip=0): ").strip()
                    if raw == "":
                        pass
                    elif raw.lower() == "s":
                        relevance = 0
                    elif raw in ("0", "1"):
                        relevance = int(raw)
                    else:
                        print("Unrecognized input, keeping LLM suggestion.")
                except Exception:
                    # ignore if input isn't available
                    pass

                print(f"Annotation for rank {rank} id={h.get('_id')}: relevance={relevance}\n")
                save_annotation({
                    "query_id": qid,
                    "index": index,
                    "result_id": h.get("_id"),
                    "rank": rank,
                    "relevance": relevance
                }, annotations_path)
    finally:
        if scheduler and not human_mode:
            scheduler.stop()

def save_annotation(obj: Dict[str, Any], annotations_path: str):
    os.makedirs(os.path.dirname(annotations_path), exist_ok=True)
    with open(annotations_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

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


def load_queries(query_file: str = None) -> List[Dict[str, Any]]:
    """Load queries from a JSON file. If no file is provided, load default queries.json next to this script.
    Supports the original grouped format (research_papers/tables/figures) or a flat list.
    """
    path = query_file or DEFAULT_QUERIES_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Queries file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    queries: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        # handle grouped format
        for section, items in data.items():
            if isinstance(items, list):
                for it in items:
                    qid = it.get("id") or it.get("query_id") or it.get("query") or f"{section}-{int(time.time())}"
                    queries.append({
                        "id": qid,
                        "index": it.get("index") or section,
                        "query": it.get("query"),
                        "query_body": it.get("query_body")
                    })
    elif isinstance(data, list):
        for it in data:
            qid = it.get("id") or it.get("query_id") or it.get("query") or str(int(time.time()))
            queries.append({
                "id": qid,
                "index": it.get("index"),
                "query": it.get("query"),
                "query_body": it.get("query_body")
            })
    else:
        raise ValueError("Unsupported queries.json format")

    return queries

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
    precisions = []
    aps = []
    ndcgs = []
    for qid, rels in ann.items():
        print(f"Metrics for query_id={qid} with relevances={rels}")
        precisions.append(precision_at_k(rels, k))
        aps.append(average_precision(rels))
        ndcgs.append(ndcg_at_k(rels, k))
    if not precisions:
        print("No annotations found.")
        return
    print(f"Precision@{k}: {sum(precisions)/len(precisions):.4f}")
    print(f"MAP: {sum(aps)/len(aps):.4f}")
    print(f"nDCG@{k}: {sum(ndcgs)/len(ndcgs):.4f}")

def main(query_file: str = None, top_k: int = 10, annotations_path: Optional[str] = None, human_mode: bool = False):
    if query_file:
        queries = load_queries(query_file)
    else:
        queries = load_queries()
    # ensure annotations_path is set (created by run_queries if None)
    if annotations_path is None:
        annotations_path = make_default_annotations_path()
    #run_queries(queries, top_k, annotations_path=annotations_path, human_mode=human_mode)
    compute_metrics(top_k, annotations_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run queries and annotate search results (LLM + optional human in the loop)")
    parser.add_argument("query_file", nargs="?", help="Path to queries.json")
    parser.add_argument("--top_k", "-k", type=int, default=10, help="Number of top results to fetch per query")
    parser.add_argument("--output", "-o", help="Annotations output file (jsonl). If omitted, a timestamped file will be created next to this script.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enable human-in-the-loop confirmation/override of LLM annotations")
    args = parser.parse_args()

    main(args.query_file, args.top_k, annotations_path=args.output, human_mode=args.interactive)
