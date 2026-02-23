import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename='link.log')
logger = logging.getLogger(__name__)

import components.linker.common as linker_common
import components.linker.arxiv as linker_arxiv
import components.linker.pubmed as linker_pubmed

def main():
    print("Linking documents...")
    linker_common.link("output/arxiv", linker_arxiv.linker)
    linker_common.link("output/pubmed", linker_pubmed.linker)
    print("Linking completed.")

if __name__ == "__main__":
    main()