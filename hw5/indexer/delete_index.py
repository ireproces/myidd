import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename= "delete_index.log")
logger = logging.getLogger(__name__)


from components.indexer import Indexer



def main():
    indexer: Indexer = Indexer("research_papers")
    indexer.delete_index()
    indexer = Indexer("figures")
    indexer.delete_index()
    indexer = Indexer("tables")
    indexer.delete_index()


if __name__ == "__main__":
    main()