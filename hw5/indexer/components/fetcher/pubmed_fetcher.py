import httpx
import lxml.etree as ET
import json
import os
import logging
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

source_folder_name = "output/pubmed"
cache_folder_name = "cache"
time_to_next_request = 0.12  # seconds
api_key = os.getenv("NCBI_API_KEY", None)
if api_key:
    logger.info("Using NCBI API key for requests.")
else:
    logger.info("No NCBI API key found. Requests will be limited to 3 per second.")
    time_to_next_request = 0.34  # seconds

def _format_seconds(sec: float) -> str:
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

def save_metadata_as_json(metadata: dict, filename: str) -> bool:
    with open(filename, 'w') as f:
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

#UNUSED
async def download_pmc_xml(pmcid: str, client: httpx.AsyncClient) -> bool:
    if api_key:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml&api_key={api_key}"
    else:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml"
    response = await client.get(url)
    logger.info(f"Fetched PMC XML for {pmcid}. URL: {url} Status code: {response.status_code}")
    return response

async def fetch_pubmed_central(query: str, max_results: int = 10, start: int = 0, client: httpx.AsyncClient = None, driver: webdriver.Chrome = None) -> int:
      # Wait for the page to load
    
    if api_key:
        search_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={query}"
            f"&retstart={start}&retmax={max_results}&retmode=json&api_key={api_key}"
        )
    else:
        search_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={query}"
            f"&retstart={start}&retmax={max_results}&retmode=json"
        )
    logger.info(f"Fetching PMC search URL: {search_url}")
    search_response = await client.get(search_url)
    logger.info(f"Response status code: {search_response.status_code}")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
    await asyncio.sleep(time_to_next_request)
    entry_count = 0
    if search_response.status_code == 200:
        search_data = search_response.json()
        id_list = search_data.get('esearchresult', {}).get('idlist', [])
        entry_count = len(id_list)
        logger.info(f"Found {entry_count} PMC IDs.")
        if entry_count == 0:
            logger.info("No more entries found in PMC search response.")
        for pmcid in id_list:
            filename_base = pmcid
            if not exists_paper(f"{filename_base}.json") and not in_cache(f"{filename_base}.cache"):
                fetch_response = await download_pmc_xml(pmcid, client)
                #selenium_url = f"http://pmc.ncbi.nlm.nih.gov/articles/PMC{pmcid}/"
                #driver.get(selenium_url)
                #selenium_response = driver.page_source
                #logger.info(f"Fetched PMC article page for {pmcid} using Selenium. URL: {selenium_url}")
                if fetch_response.status_code == 200 and fetch_response.content.strip():
                    root = ET.fromstring(fetch_response.content)
                    article = root.find('.//article')
                    title = ""
                    summary = ""
                    authors = []
                    published = ""
                    if article is not None:
                        title_elem = article.find('.//article-title')
                        if title_elem is not None:
                            title = "".join(title_elem.itertext()).strip()
                        abstract_elem = article.find('.//abstract')
                        if abstract_elem is not None:
                            summary = "".join(abstract_elem.itertext()).strip()
                        for contrib in article.findall('.//contrib[@contrib-type="author"]'):
                            name_elem = contrib.find('name')
                            if name_elem is not None:
                                surname = name_elem.findtext('surname', default='')
                                given_names = name_elem.findtext('given-names', default='')
                                full = f"{given_names} {surname}".strip()
                                if full:
                                    authors.append(full)
                        pubdate_elem = article.find('.//pub-date')
                        if pubdate_elem is not None:
                            year = pubdate_elem.findtext('year', default='')
                            published = f"{year}"
                    link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
                    metadata = {
                        "title": title,
                        "authors": authors,
                        "published": published,
                        "summary": summary,
                        "link": link
                    }
                    relative_path = os.path.join(source_folder_name, filename_base)
                    #with open(f"{relative_path}.html", 'wb') as f:
                        #f.write(selenium_response.encode('utf-8'))
                    #logger.info(f"Downloaded and saved PMC article {relative_path}.html using Selenium")
                    with open(f"{relative_path}.xml", 'wb') as f:
                        f.write(fetch_response.content)
                    logger.info(f"Downloaded and saved PMC article {relative_path}.xml")
                    save_metadata_as_json(metadata, f"{relative_path}.json")
                    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
                    await asyncio.sleep(time_to_next_request)
                else:
                    logger.warning(f"Failed to fetch metadata/fulltext for PMC ID {pmcid}. Status code: {fetch_response.status_code}")
            else:
                if exists_paper(f"{filename_base}.json"):
                    logger.info(f"Paper {filename_base} already exists. Skipping download.")
                if in_cache(f"{filename_base}.cache"):
                    logger.info(f"Paper {filename_base} is in cache. Skipping download.")
                await asyncio.sleep(0) # yield control to event loop
    else:
        logger.error(f"Error fetching data from PMC: {search_response.status_code}")
        logger.error(search_response.text)
    logger.info("Finished processing current batch from PMC.")
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

    done = False

    options = Options()
    options.add_argument("--headless=new")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    async with httpx.AsyncClient() as client:
        while processed < total and not done:
            entry_count = await fetch_pubmed_central(query, max_results, processed, client, driver)
            logger.info(f"Fetched {processed}+{entry_count} of {total} results.")
            processed += entry_count
            if entry_count == 0:
                logger.info("No more entries to process from PMC. Ending fetch.")
                done = True
    driver.quit()
    total_elapsed = asyncio.get_event_loop().time() - start_time
    logger.info(f"Completed fetch of {total} items in {_format_seconds(total_elapsed)}.")