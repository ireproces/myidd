import tkinter as tk
from tkinter import scrolledtext
from elasticsearch import Elasticsearch
import re
import webbrowser
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")


index_options = ["research_papers","figures","tables"]

def parse_query(user_query, index_name):
    # Date range: published:>2020, published:>=2021-03, published:<2022-01-15, etc.
    date_range = re.search(r'published\s*:\s*([<>]=|[<>]|=)\s*([\d\-]+)', user_query)
    if date_range:
        op, date_val = date_range.groups()
        logger.info(f"Date range detected: op={op}, date_val={date_val}")
        op_map = {'>': 'gt', '>=': 'gte', '<': 'lt', '<=': 'lte', '=': 'eq'}
        if op == '=':
            # If only year is given, search for that year
            if len(date_val) == 4:
                logger.info(f"Exact year query: date_val={date_val}")
                return {
                    "range": {
                        "published": {
                            "gte": f"{date_val}-01-01",
                            "lt": f"{int(date_val)+1}-01-01"
                        }
                    }
                }
            # If year and month are given
            elif len(date_val) == 7:
                year, month = date_val.split('-')
                next_month = int(month) + 1
                if next_month > 12:
                    next_month = 1
                    next_year = int(year) + 1
                else:
                    next_year = int(year)
                
                logger.info(f"Exact month query: year={year}, month={month}, next_year={next_year}, next_month={next_month}")
                return {
                    "range": {
                        "published": {
                            "gte": f"{year}-{month}-01",
                            "lt": f"{next_year}-{next_month:02d}-01"
                        }
                    }
                }
            else:
                # Exact date
                logger.info(f"Exact date query: date_val={date_val}")
                return {"term": {"published": date_val}}
        else:
            logger.info(f"Date range query: op={op}, op_map_result={op_map[op]}, date_val={date_val}")
            return {"range": {"published": {op_map[op]: date_val}}}

    # Field-specific queries: field:"query"
    field_queries = re.findall(r'(\w+):"([^"]+)"', user_query)
    # Boolean operators
    if " OR " in user_query:
        clauses = []
        for field, value in field_queries:
            clauses.append({"match": {field: value}})
        return {"bool": {"should": clauses}}
    elif " AND " in user_query:
        clauses = []
        for field, value in field_queries:
            clauses.append({"match": {field: value}})
        return {"bool": {"must": clauses}}
    elif field_queries:
        # Single field query
        field, value = field_queries[0]
        return {"match": {field: value}}
    else:
        # Default: search all fields
        fields = ["title", "authors", "summary", "content"]
        if index_name == "figures":
            fields = ["figure_id", "caption", "paper_id", "url", "blob_data"]
        elif index_name == "tables":
            fields = ["table_id", "description", "paper_id", "data", "table_url", "blob_data"]
            
        return {"multi_match": {"query": user_query, "fields": fields}}

def search():
    query = entry.get()
    if not query:
        return
    current_index = selected_index.get()
    result_box.config(state=tk.NORMAL)
    result_box.delete(1.0, tk.END)
    try:
        es_query = parse_query(query, current_index)
        res = es.search(index=current_index, query=es_query)
        print(f"Elasticsearch query: {es_query}")
        #print(f"Elasticsearch response: {res}")
        hits = res['hits']['hits']
        if not hits:
            result_box.insert(tk.END, "No results found.\n")
        for i, hit in enumerate(hits):
            source = hit['_source']
            link = 'N/A'
            
            if current_index == "figures":
                result_box.insert(tk.END, f"Figure ID: {source.get('figure_id', 'N/A')}\n")
                result_box.insert(tk.END, f"Caption: {source.get('caption', 'N/A')}\n")
                link = source.get('url', 'N/A')
            elif current_index == "tables":
                result_box.insert(tk.END, f"Table ID: {source.get('table_id', 'N/A')}\n")
                result_box.insert(tk.END, f"Caption: {source.get('caption', 'N/A')}\n")
                link = source.get('table_url', 'N/A')
            else:
                # Default research papers
                result_box.insert(tk.END, f"Title: {source.get('title', 'N/A')}\n")
                result_box.insert(tk.END, f"Authors: {', '.join(source.get('authors', []))}\n")
                result_box.insert(tk.END, f"Published: {source.get('published', 'N/A')}\n")
                link = source.get('link', 'N/A')

            if link != 'N/A':
                start = result_box.index(tk.END)
                result_box.insert(tk.END, f"Link: {link}\n\n")
                end = result_box.index(tk.END)
                tag_name = f"link{i}"
                result_box.tag_add(tag_name, f"{float(start)-1} linestart+6c", f"{float(start)-1} lineend")
                result_box.tag_config(tag_name, foreground="blue", underline=1)
                result_box.tag_bind(tag_name, "<Button-1>", lambda e, url=link: webbrowser.open(url))
            else:
                result_box.insert(tk.END, "Link: N/A\n\n")
    except Exception as e:
        result_box.insert(tk.END, f"Error: {e}\n")
    result_box.config(state=tk.NORMAL)



root = tk.Tk()
root.title("Elasticsearch Search Engine")
selected_index = tk.StringVar(value=index_options[0])
tk.Label(root, text="Select index:").pack(pady=5, anchor="w")
index_menu = tk.OptionMenu(root, selected_index, *index_options)
index_menu.pack(pady=5, fill="x", padx=10)


tk.Label(root, text="Enter your search query:").pack(pady=5, anchor="w")
entry = tk.Entry(root)
entry.pack(pady=5, fill="x", padx=10, expand=True)

tk.Button(root, text="Search", command=search).pack(pady=5)

result_box = scrolledtext.ScrolledText(root)
result_box.pack(pady=10, fill="both", expand=True, padx=10)

root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)
root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)

root.mainloop()