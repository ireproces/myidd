import logging

logger = logging.getLogger(__name__)

import bs4
from domain.paragraph import Paragraph


def extract_paragraphs_from_html(html_content: str, paper_id: str) -> list[Paragraph]:
    # Placeholder for actual HTML parsing and paragraph extraction logic
    paragraphs = []
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    # extract all paragraph with class ltx_p
    para_tags = soup.find_all('p', class_='ltx_p')
    for tag in para_tags:
        paragraph_text = tag.decode_contents().strip()
        paragraph_id = tag.get('id', 'unknown_id')
        paragraphs.append(Paragraph(paper_id, paragraph_id, paragraph_text))
    return paragraphs