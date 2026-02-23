import os
import json
import components.html_cleaner as html_cleaner
import logging

logger = logging.getLogger(__name__)

def collect_papers(directory_path:str) -> list[str]:
    papers = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".html") or filename.endswith(".xml"):
            #print(f"Found paper file: {filename}")
            papers.append(filename)
    #print(f"Collected {len(papers)} papers from directory: {directory_path}")
    return papers

def load_research_papers_data_from_directory(directory_path: str) -> iter:
    for filename in collect_papers(directory_path):
        try:
            if filename:
                metadata_filename = ""
                if filename.endswith(".html"):
                    metadata_filename = filename.replace(".html", ".json")
                elif filename.endswith(".xml"):
                    metadata_filename = filename.replace(".xml", ".json")
                #print(metadata_filename)
                metadata_file_path = os.path.join(directory_path, metadata_filename)
                file_path = os.path.join(directory_path, filename)
                with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
                    with open(file_path, 'r', encoding='utf-8') as content_file:
                        content = content_file.read()
                        content = html_cleaner.clean_html(content)
                        #print(content)
                        metadata = json.load(metadata_file)
                        document = {
                            "title": metadata.get("title", ""),
                            "authors": metadata.get("authors", []),
                            "published": metadata.get("published", ""),
                            "summary": metadata.get("summary", ""),
                            "link": metadata.get("link", ""),
                            "content": content
                        }
                        logger.info(f"Loaded document: {metadata.get('title', 'N/A')}. Paper content size: {len(content)} characters.")
                        #print(f"{document['title']}")
                        yield document
        except Exception as e:
            logger.error(f"Error loading document from file {filename}: {e}")

def load_figures_data_from_directory(directory_path: str) -> iter:
    for filename in collect_papers(directory_path):
        try:
            clean_filename = filename.replace(".html", "").replace(".xml", "")
            figures_filename = f"{clean_filename}_figures.json"
            paragraphs_filename = f"{clean_filename}_paragraphs.json"
            links_filename = f"{clean_filename}_links.json"
            
            figures_path = os.path.join(directory_path, figures_filename)
            paragraphs_path = os.path.join(directory_path, paragraphs_filename)
            links_path = os.path.join(directory_path, links_filename)

            if os.path.exists(figures_path) and os.path.exists(paragraphs_path) and os.path.exists(links_path):
                with open(figures_path, 'r', encoding='utf-8') as f:
                    figures_data = json.load(f)
                    logger.info(f"Loaded {len(figures_data)} figures from file: {figures_path}")
                with open(paragraphs_path, 'r', encoding='utf-8') as f:
                    paragraphs_data = json.load(f)
                    logger.info(f"Loaded {len(paragraphs_data)} paragraphs from file: {paragraphs_path}")
                with open(links_path, 'r', encoding='utf-8') as f:
                    links_data = json.load(f)
                    logger.info(f"Loaded {len(links_data)} links from file: {links_path}")
                for figure in figures_data:
                    figure_id = figure.get("figure_id")
                    
                    referencing_text = []
                    links = links_data.get(figure_id, [])
                    logger.info(f"Figure {figure_id} has {len(links)} links referencing it.")
                    if links:
                        for paragraph in paragraphs_data:
                            paragraph_id = paragraph.get("paragraph_id")
                            text = paragraph.get("text", "")
                            #clean the text to remove HTML tags and special characters
                            text = html_cleaner.clean_html(text)
                            # Check if the paragraph contains any of the IDs that link to this figure
                            if paragraph_id in links:
                                referencing_text.append(text)
                            
                    blob_data = "\n".join(referencing_text)
                    blob_data = html_cleaner.clean_html(blob_data)

                    logger.info(f"Loaded figure: {figure_id}. Referencing text size: {len(blob_data)} characters.")

                    yield {
                        "figure_id": figure_id,
                        "caption": html_cleaner.clean_html(figure.get("caption")),
                        "paper_id": figure.get("paper_id"),
                        "url": figure.get("url"),
                        "image_url": figure.get("image_url"),
                        "blob_data": blob_data
                    }

        except Exception as e:
            logger.error(f"Error loading figure data from file {filename}: {e}")

def load_tables_data_from_directory(directory_path: str) -> iter:
    for filename in collect_papers(directory_path):
        try:
            clean_filename = filename.replace(".html", "").replace(".xml", "")
            tables_filename = f"{clean_filename}_tables.json"
            paragraphs_filename = f"{clean_filename}_paragraphs.json"
            links_filename = f"{clean_filename}_links.json"
            
            tables_path = os.path.join(directory_path, tables_filename)
            paragraphs_path = os.path.join(directory_path, paragraphs_filename)
            links_path = os.path.join(directory_path, links_filename)

            if os.path.exists(tables_path) and os.path.exists(paragraphs_path) and os.path.exists(links_path):
                with open(tables_path, 'r', encoding='utf-8') as f:
                    tables_data = json.load(f)
                
                with open(paragraphs_path, 'r', encoding='utf-8') as f:
                    paragraphs_data = json.load(f)
                
                with open(links_path, 'r', encoding='utf-8') as f:
                    links_data = json.load(f)

                for table in tables_data:
                    table_id = table.get("table_id")
                    
                    referencing_text = []
                    links = links_data.get(table_id, [])
                    logger.info(f"Table {table_id} has {len(links)} links referencing it.")
                    if links:
                        for paragraph in paragraphs_data:
                            paragraph_id = paragraph.get("paragraph_id")
                            text = paragraph.get("text", "")
                            #clean the text to remove HTML tags and special characters
                            text = html_cleaner.clean_html(text)
                            # append only those paragraphs that the link file associates with this table
                            if paragraph_id in links:
                                referencing_text.append(text)

                            
                    blob_data = "\n".join(referencing_text)
                    blob_data = html_cleaner.clean_html(blob_data)

                    logger.info(f"Loaded table: {table_id}. Referencing text size: {len(blob_data)} characters.")
                    yield {
                        "table_id": table_id,
                        "caption": html_cleaner.clean_html(table.get("caption")),
                        "paper_id": table.get("paper_id"),
                        "data": html_cleaner.clean_html(table.get("data")),
                        "table_url": table.get("table_url"),
                        "blob_data": blob_data
                    }
        except Exception as e:
            logger.error(f"Error loading table data from file {filename}: {e}")

