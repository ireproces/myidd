import logging

logger = logging.getLogger(__name__)

import bs4
from domain.paragraph import Paragraph

def extract_paragraphs_from_xml(xml_content: str, paper_id: str) -> list[Paragraph]:
    paragraphs = []
    # Use 'xml' or 'lxml-xml' parser for PubMed files
    soup = bs4.BeautifulSoup(xml_content, 'xml') 
    
    # Find all paragraphs
    tags = soup.find_all('p')
    
    for i, tag in enumerate(tags):
        text = tag.decode_contents().strip()
        para_id = f"{paper_id}_para_{i+1}"
        if text:
            paragraphs.append(Paragraph(paper_id, para_id, text))
            
    return paragraphs