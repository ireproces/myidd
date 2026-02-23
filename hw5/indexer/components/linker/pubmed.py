import logging

logger = logging.getLogger(__name__)

import bs4

def parse_references(paragraph_text: str) -> list[str]:
    soup = bs4.BeautifulSoup(paragraph_text, 'html.parser')
    references = []
    for xref in soup.find_all('xref'):
        ref_id = xref.get('rid', '').strip()
        logger.info(f"Found reference: {ref_id}")
        if ref_id:
            references.append(ref_id)
    return references

def linker(paragraphs: list[str], figures: list[str], tables: list[str]):
    result = {}
    for p in paragraphs:
        references = parse_references(p['text'])
        logger.info(f"Paragraph {p['paragraph_id']} references: {references}")
        for f in figures:
            for reference in references:
                if f['figure_id'] in reference:
                    # Link the figure to the paragraph
                    logger.info(f"Linking figure {f['figure_id']} to paragraph {p['paragraph_id']}")
                    if f['figure_id'] not in result:
                        result[f['figure_id']] = []
                    result[f['figure_id']].append(p['paragraph_id'])
        for t in tables:
            for reference in references:
                if t['table_id'] in reference:
                    # Link the table to the paragraph
                    logger.info(f"Linking table {t['table_id']} to paragraph {p['paragraph_id']}")
                    if t['table_id'] not in result:
                        result[t['table_id']] = []
                    result[t['table_id']].append(p['paragraph_id'])
    return result