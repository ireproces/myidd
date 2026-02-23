import logging

logger = logging.getLogger(__name__)

import components.utils as utils
import os
import json

def linker(paper: str, linker_function: function = None):
    logger.info(f"Linking {paper}...")
    paragraphs_file = f"{paper}_paragraphs.json"
    figures_file = f"{paper}_figures.json"
    tables_file = f"{paper}_tables.json"
    if os.path.exists(paragraphs_file) and os.path.exists(figures_file) and os.path.exists(tables_file):
        with open(paragraphs_file, 'r') as f:
            paragraphs = json.load(f)
        with open(figures_file, 'r') as f:
            figures = json.load(f)
        with open(tables_file, 'r') as f:
            tables = json.load(f)
        # Implement your linking logic here
        links = linker_function(paragraphs, figures, tables)
        # create link output file
        output_file = f"{paper}_links.json"
        with open(output_file, 'w') as f:
            json.dump(links, f, indent=4)
        logger.info(f"Linked {len(paragraphs)} paragraphs, {len(figures)} figures, and {len(tables)} tables for {paper}.")
    else:
        logger.warning(f"Missing files for {paper}. Skipping linking.")


def link(data_path: str, linker_function: function = None):
    logger.info("Linking...")
    paper = utils.collect_papers(data_path)
    for paper in paper:
        linker(paper, linker_function)
    logger.info("Linking completed.")