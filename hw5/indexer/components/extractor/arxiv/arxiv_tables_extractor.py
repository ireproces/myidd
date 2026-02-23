import logging

logger = logging.getLogger(__name__)

import bs4
from domain.table import Table


def extract_table_from_html(html_content: str, paper_id: str) -> list[Table]:
    # Placeholder for actual HTML parsing and paragraph extraction logic
    tables = []
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    # extract all paragraph with class ltx_p
    table_tags = soup.find_all("figure", class_='ltx_figure')
    for table_tag in table_tags:
        caption_tag = table_tag.find('figcaption', class_='ltx_caption')
        data_tag = table_tag.find('table')
        if caption_tag and data_tag:
            caption_text = caption_tag.decode_contents().strip()
            data = str(data_tag)
            table_id = table_tag.get('id', 'unknown_id')
            table_url = f"https://arxiv.org/html/{paper_id}#{table_id}"
            tables.append(Table(paper_id, table_id, caption_text, table_url, data))


    table_tags = soup.find_all("figure", class_='ltx_table')
    for table_tag in table_tags:
        caption_tag = table_tag.find('figcaption', class_='ltx_caption')
        data_tag = table_tag.find('table')
        if caption_tag and data_tag:
            caption_text = caption_tag.decode_contents().strip()
            data = str(data_tag)
            table_id = table_tag.get('id', 'unknown_id')
            table_url = f"https://arxiv.org/html/{paper_id}#{table_id}"
            tables.append(Table(paper_id, table_id, caption_text, table_url , data))
    return tables