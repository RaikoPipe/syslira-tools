from syslira_tools import ZoteroClient, OpenAlexClient, PaperLibrary
from loguru import logger
import os

# load environment variables from .env file if exists
from dotenv import load_dotenv
load_dotenv()

def get_paper_collection(collection_key, get_fulltext=True):
    """Initialize the Zotero client."""

    zotero_api_key = os.environ.get("ZOTERO_API_KEY")
    zotero_library_id = os.environ.get("ZOTERO_LIBRARY_ID")
    zotero_library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")

    logger.info("Initializing Zotero client...")
    zotero_client = ZoteroClient(zotero_api_key, zotero_library_id,
                                 library_type=zotero_library_type)
    zotero_client.init()

    logger.info("Initializing OpenAlex client...")
    openalex_client = OpenAlexClient()
    openalex_client.init()

    # Set up paper library
    paper_library = PaperLibrary(
        zotero_client=zotero_client,
        openalex_client=openalex_client,
        collection_key=collection_key,
    )

    # get papers
    result = paper_library.update_from_zotero(get_fulltext=get_fulltext, deduplicate=False)
    logger.info(result)

    return paper_library.get_library_df()

def save_fulltext_as_file(paper_collection, path="./"):
    """Save fulltext of literature items collection to textfile."""

    for idx, paper in paper_collection.iterrows():
        filename = f"{paper['title'].replace('/', '_')}.txt"
        # make dir if not exists
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+filename, 'w', encoding='utf-8') as f:
            f.write(paper['fulltext'])
        logger.info(f"Saved full text of '{paper['title']}' to '{filename}'")

if __name__ == "__main__":
    collection_key = os.environ.get("ZOTERO_COLLECTION_KEY")
    paper_collection = get_paper_collection(collection_key=collection_key, get_fulltext=True)
    save_fulltext_as_file(paper_collection, path="./fulltexts/")