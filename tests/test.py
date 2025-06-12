from unittest import TestCase  #
import os
import pandas as pd

from syslira_tools import PaperLibrary, ZoteroClient, OpenAlexClient
from const import PROJECT_PATH

import json
from loguru import logger
from const import UNION_COLUMNS
from syslira_tools.helpers import convert_inverted_index

with open(f"{PROJECT_PATH}/tests/example_papers.json") as f:
    example_papers = json.load(f)

# get zotero library env variables
zotero_api_key = os.environ.get("ZOTERO_API_KEY", None)
zotero_library_id = os.environ.get("ZOTERO_LIBRARY_ID", None)
zotero_collection_key = os.environ.get("ZOTERO_COLLECTION_KEY", None)
zotero_library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")

if not zotero_api_key:
    zotero_api_key = input("Please enter your Zotero API key: ")
if not zotero_library_id:
    zotero_library_id = input("Please enter your Zotero library ID: ")
while zotero_library_type not in ["user", "group"]:
    zotero_library_type = input("Please enter your Zotero library type (user or group): ")
    if zotero_library_type not in ["user", "group"]:
        print("Invalid library type. Please enter 'user' or 'group'.")
if not zotero_collection_key:
    zotero_collection_key = input("Please enter your Zotero collection key (optional, press Enter to skip): ")
    zotero_collection_key = zotero_collection_key if zotero_collection_key else None

zotero_client = ZoteroClient()
zotero_client.init()
openalex_client = OpenAlexClient()
paper_library = PaperLibrary(zotero_client, openalex_client)


# class ScopusRetrievalTestCase(TestCase):
#     def test_01_search_and_add_to_library(self):
#         syslira.retrieve_and_add_papers_to_library(
#             "TITLE-ABS-KEY(generative AND ai AND simulation AND modeling) AND PUBYEAR > 2020 AND SUBJAREA(COMP) AND (DOCTYPE(ar) or DOCTYPE(cp))"
#         )
#         self.assertTrue(True)
#
#     def test_02_add_to_zotero_library(self):
#         syslira.init_zotero_client(library_type="user")
#         message = syslira.update_zotero_library()
#         self.assertTrue(message)
#         self.assertIsInstance(message, str)
#         self.assertTrue(message)
#
#
# class ZoteroRetrievalTestCase(TestCase):
#     def test_01_update_local_w_zotero(self):
#         syslira_manager.init_zotero_client()
#         self.assertTrue(True)
#
#     def test_02_update_zotero_w_local(self):
#         syslira_manager.update_zotero_library()
#         self.assertTrue(True)
#
#     def test_03_get_zotero_attachments(self):
#         syslira.init_zotero_client()
#         papers_library = syslira.get_paper_library_dataframe()
#         syslira.retrieve_full_text_for_item(papers_library.iloc[0]["item_key"])
#         self.assertTrue(True)

class HelpersTestCase(TestCase):
    def test_01_get_abstract_inverted_index(self):
        example_abstact_inverted_index = {
            "Generative": [0],
            "AI": [1],
            "is": [2],
            "capable": [3],
            "of": [4],
            "performing": [5],
            "tasks": [6, 15],
            "that": [7, 16],
            "require": [8, 17],
            "human": [9],
            "level": [10],
            "intelligence": [11],
            ",": [12],
            "such": [13],
            "as": [14],
            "step-by-step": [18],
            "reasoning": [19],
            ".": [20],
        }
        reference = "Generative AI is capable of performing tasks that require human level intelligence, such as tasks that require step-by-step reasoning."
        result = convert_inverted_index(example_abstact_inverted_index)

        self.assertEqual(result, reference)

class PaperLibraryTestCase(TestCase):

    def setUp(self):
        self.paper_library = paper_library

    def test_01_add_paper_to_library(self):
        self.paper_library.papers_df = pd.DataFrame()
        self.paper_library.add_papers_to_library(
            papers=example_papers,
        )
        self.assertTrue(len(self.paper_library.get_library_df().index) > 0)
        self.assertTrue(True)

    def test_02_update_papers_in_library(self):
        # remove some papers to test update
        self.paper_library.papers_df = self.paper_library.papers_df.iloc[0:3]
        result = self.paper_library.add_papers_to_library(
            papers=example_papers,
        )
        self.assertTrue(len(self.paper_library.get_library_df().index) > 3)

    def test_02_get_paper_text(self):
        paper_text = zotero_client.get_fulltext(
            item_key=example_papers[0]["id"]
        )
        self.assertTrue(isinstance(paper_text, str))
        self.assertTrue(True)


# class OpenalexRetrievalTestCase(TestCase):
#     def setUp(self):
#         self.paper_library = _get_paper_library()
#
#     def test_01_search_and_add_to_library(self):
#         self.paper_library.papers_df = self.paper_library.papers_df.iloc[:0]  # Clear the DataFrame for testing
#         filter_args = {
#             "publication_year": "2023-2025",
#             "type": "article",
#             "cited_by_count": 0
#         }
#         papers = paper_library.retrieve_papers(
#             query={
#                 "title_and_abstract": "(domain-specific OR domain-adapted) AND ('generative AI' OR "
#                                       "'generative artificial intelligence' OR LLM OR 'large language model')"
#             },
#             filter_args=filter_args,
#         )
#         self.assertTrue(papers)
#
#     def test_02_get_count_search_results(self):
#         filter_args = {
#             "publication_year": "2023-2025",
#             "type": "article",
#             "cited_by_count": 0,
#         }
#         message = syslira_manager.get_result_count(
#             query={
#                 "title_and_abstract": "(domain-specific OR domain-adapted) AND ('generative AI' OR "
#                                       "'generative artificial intelligence' OR LLM OR 'large language model')"
#             },
#             platform="openalex",
#             filter_args=filter_args,
#         )
#         print(message)
#         self.assertTrue(message)
#
#     def test_03_sync_libraries(self):
#         syslira_manager.init_zotero_client(library_type="user")
#         self.paper_library.add_papers_to_library(
#             papers=example_papers,
#         )
#         message = syslira_manager.sync_zotero_collection(collection_key="NI94JZZ5")
#         if message:
#             logger.info(f"Zotero collection synced: {message}")
#
#         # papers_df should still have required columns after sync
#         has_columns = set(self.paper_library.get_library_df().columns.to_list())
#         requires_columns = set(UNION_COLUMNS)
#         logger.info(f"Difference columns: {has_columns.symmetric_difference(requires_columns)}")
#         self.assertTrue(has_columns.issubset(requires_columns))
#         # papers_df should not be empty after sync
#         self.assertTrue(self.paper_library.get_library_df().empty is False)
#         self.assertTrue(message)


if __name__ == "__main__":
    import unittest

    # Define Test Suite
    test_suite = unittest.TestSuite()
    # test_suite.addTest(unittest.makeSuite(ScopusRetrievalTestCase))
    # test_suite.addTest(unittest.makeSuite(ZoteroRetrievalTestCase))
    #test_suite.addTest(unittest.makeSuite(OpenalexRetrievalTestCase))

    # Run the tests
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
