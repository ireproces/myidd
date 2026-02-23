import logging

logger = logging.getLogger(__name__)

import os

def collect_papers(data_path: str) -> list[str]:
    output = []
    if os.path.exists(data_path):
        for f in os.listdir(data_path):
            if f.endswith('.html') or f.endswith(".xml") : #Non universale, perchè pubmed usa .xml
                logger.info(f"Found: {os.path.join(data_path, f)}")
                output.append(os.path.join(data_path, f).replace(".html", "").replace(".xml", ""))
    logger.info(f"Total files collected: {len(output)}")
    return output