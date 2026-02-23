import logging

logger = logging.getLogger(__name__)

import bs4
from domain.table import Table

def extract_tables_from_xml(xml_content: str, paper_id: str) -> list[Table]:
    tables = []
    soup = bs4.BeautifulSoup(xml_content, 'xml')
    
    # PubMed uses table-wrap for floating tables
    table_wraps = soup.find_all('table-wrap')
    for wrap in table_wraps:
        table_id = wrap.get('id')
        
        caption_tag = wrap.find('caption')
        caption_text = caption_tag.get_text().strip() if caption_tag else ""
        
        # The actual data is usually in a <table> tag inside the wrap
        data_tag = wrap.find('table') 
        data_content = str(data_tag) if data_tag else ""
        
        table_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{paper_id}/#{table_id}"

        tables.append(Table(paper_id, table_id, caption_text, table_url, data_content))

    return tables