import httpx
import lxml.etree as ET
import json
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

source_folder_name = "output/arxiv"
cache_folder_name = "cache"

time_to_next_request = 3  # seconds

def _format_seconds(sec: float) -> str:
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

def save_metadata_as_json(metadata: dict, filename: str) -> bool:
    file_relative_path = os.path.join(source_folder_name, filename)
    with open(file_relative_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    return True

def in_cache(filename: str) -> bool:
    result = False
    cache_path = os.path.join(source_folder_name, cache_folder_name)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    filepath = os.path.join(cache_path, filename)
    if os.path.exists(filepath):
        result = True
    else:
        with open(filepath, 'w') as f:
            f.write('1')
    return result

def exists_paper(filename: str) -> bool:
    return os.path.exists(os.path.join(source_folder_name, filename))

async def download_paper(url: str, filename: str, client: httpx.AsyncClient) -> bool:
    response = await client.get(url)
    file_relative_path = os.path.join(source_folder_name, filename)
    if response.status_code == 200:
        with open(file_relative_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        logger.warning(f"Failed to download paper from {url}. Status code: {response.status_code}. Skipping...")
        return False

async def calculate_actual_total(query: str, max_results: int, client: httpx.AsyncClient) -> int:
    search_query = f"all:{query}"
    url=f'https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={max_results}'
    response = await client.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        total_results = int(root.find('atom:totalResults', ns).text)
        return min(total_results, max_results)
    else:
        logger.error(f"Error fetching total results from arXiv API: {response.status_code}")
        return 0

async def fetch_arxiv(query: str, max_results: int = 10, start: int = 0, client: httpx.AsyncClient = None) -> int:
    search_query = f"all:{query}"
    url=f'https://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={max_results}'
    logger.info(f"Fetching arXiv API URL: {url}")
    response = await client.get(url)
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
    await asyncio.sleep(time_to_next_request)
    entry_count: int = 0
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entry_count = len(root.findall('atom:entry', ns))
        logger.info(f"Parsing {entry_count} entries from arXiv API response.")
        if entry_count == 0:
            logger.info("No more entries found in arXiv API response.")

        for entry in root.findall('atom:entry', ns):
            title = (entry.find('atom:title', ns).text or '').strip()
            summary = (entry.find('atom:summary', ns).text or '').strip()
            published = (entry.find('atom:published', ns).text or '').strip()
            arxiv_id = (entry.find('atom:id', ns).text or '').strip()
            authors = [a.text for a in entry.findall('atom:author/atom:name', ns)]
            link: str = next((l.get('href') for l in entry.findall('atom:link', ns) if l.get('rel') == 'alternate'), "")
            html_link = link.replace('abs', 'html').replace("arxiv", "export.arxiv") if link else None
            filename_base = arxiv_id.split('/')[-1]
            if not exists_paper(f"{filename_base}.json") and not in_cache(f"{filename_base}.cache"):
                response_status = await download_paper(html_link, f"{filename_base}.html", client) if html_link else None
                if response_status:
                    metadata = {"title": title,"authors": authors,"published": published, "summary": summary,"link": link or arxiv_id}
                    save_metadata_as_json(metadata, f"{filename_base}.json")
                    logger.info(f"Downloaded and saved paper {filename_base}")
                logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
                await asyncio.sleep(time_to_next_request)
            else:
                if exists_paper(f"{filename_base}.json"):
                    logger.info(f"Paper {filename_base} already exists. Skipping download.")
                if in_cache(f"{filename_base}.cache"):
                    logger.info(f"Paper {filename_base} is in cache. Skipping download.")
                await asyncio.sleep(0) # yield control to event loop
    else:
        logger.error(f"Error fetching data from arXiv API: {response.status_code}")
        logger.error(f"response.text: {response.text}")
    logger.info("Finished processing current batch from arXiv API.")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
    await asyncio.sleep(time_to_next_request)
    return entry_count

async def fetch(query: str, total_amount: int, max_results: int = 10, start: int = 0):
    if not os.path.exists(source_folder_name):
        os.makedirs(source_folder_name)

    total = max(0, int(total_amount))
    if total == 0:
        logger.info("Nothing to fetch (total_amount is 0).")
        return

    if total <= max_results:
        max_results = total

    processed = start
    start_time = asyncio.get_event_loop().time()

    done: bool = False
    async with httpx.AsyncClient() as client:
        while processed < total and not done:
            entry_count: int = await fetch_arxiv(query, max_results, processed, client)
            logger.info(f"Fetched {processed}+{entry_count} of {total} results.")
            processed += entry_count
            if entry_count == 0:
                logger.info("No more entries to process from arXiv API. Ending fetch.")
                done = True

    total_elapsed = asyncio.get_event_loop().time() - start_time
    logger.info(f"Completed fetch of {total} items in {_format_seconds(total_elapsed)}.")