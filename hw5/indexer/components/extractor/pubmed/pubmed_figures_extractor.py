import logging

logger = logging.getLogger(__name__)

import bs4
from domain.figure import Figure

def extract_figures_from_xml(xml_content: str, paper_id: str) -> list[Figure]:
    figures = []
    soup = bs4.BeautifulSoup(xml_content, 'xml')
    
    fig_tags = soup.find_all('fig')
    for fig in fig_tags:
        figure_id = fig.get('id', 'unknown_id')
        
        caption_tag = fig.find('caption')
        caption_text = caption_tag.get_text().strip() if caption_tag else ""
        
        url = f"https://pmc.ncbi.nlm.nih.gov/articles/{paper_id}/#{figure_id}"
        image_url = fig.find('img').get('src', '') if fig.find('img') else ""
        figures.append(Figure(paper_id, figure_id, caption_text, url, image_url))
        
    return figures