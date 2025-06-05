from unittest import TestCase  #

import pandas as pd

import code_agent_tools.manager as syslira_manager
import code_agent_tools as syslira_analyst
from code_agent_tools import common
from syslira_tools.clients.const import PROJECT_PATH
from code_agent_tools import _get_paper_library
from lr_tools.helpers import convert_inverted_index
import json
from loguru import logger
from lr_tools.const import UNION_COLUMNS

with open(f"{PROJECT_PATH}/tests/example_papers.json") as f:
    example_papers = json.load(f)


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
        self.paper_library = _get_paper_library()

    def test_01_add_paper_to_library(self):
        self.paper_library.papers_df = pd.DataFrame()
        syslira_manager.init_zotero_client(library_type="user")
        self.paper_library.add_papers_to_library(
            papers=example_papers,
        )
        self.assertTrue(len(self.paper_library.get_library_df().index) > 0)
        self.assertTrue(True)

    def test_02_get_paper_text(self):
        syslira_manager.init_zotero_client(library_type="user")
        paper_text = syslira_analyst.get_paper_fulltext(
            paper_index=example_papers[0]["id"]
        )
        self.assertTrue(isinstance(paper_text, str))
        self.assertTrue(True)

    def test_03_get_paper_indices(self):
        syslira_manager.init_zotero_client(library_type="user")
        paper_indices = syslira_manager.get_paper_indices()

        self.assertTrue(len(paper_indices) > 0)

    def test_04_search_paper_index_by_title(self):
        syslira_manager.init_zotero_client(library_type="user")
        paper_index = common.search_paper_index_by_title(
            query="Large Language Model Adaptation for Financial Sentiment Analysis"
        )
        self.assertTrue(paper_index)


class OpenalexRetrievalTestCase(TestCase):
    def setUp(self):
        self.paper_library = _get_paper_library()

    def test_01_search_and_add_to_library(self):
        self.paper_library.papers_df = self.paper_library.papers_df.iloc[:0]  # Clear the DataFrame for testing
        filter_args = {
            "publication_year": "2023-2025",
            "type": "article",
            "cited_by_count": 0
        }
        papers = syslira_manager.retrieve_papers(
            query={
                "title_and_abstract": "(domain-specific OR domain-adapted) AND ('generative AI' OR "
                                      "'generative artificial intelligence' OR LLM OR 'large language model')"
            },
            platform="openalex",
            filter_args=filter_args,
        )
        self.assertTrue(papers)

    def test_02_get_count_search_results(self):
        filter_args = {
            "publication_year": "2023-2025",
            "type": "article",
            "cited_by_count": 0,
        }
        message = syslira_manager.get_result_count(
            query={
                "title_and_abstract": "(domain-specific OR domain-adapted) AND ('generative AI' OR "
                                      "'generative artificial intelligence' OR LLM OR 'large language model')"
            },
            platform="openalex",
            filter_args=filter_args,
        )
        print(message)
        self.assertTrue(message)

    def test_03_sync_libraries(self):
        syslira_manager.init_zotero_client(library_type="user")
        self.paper_library.add_papers_to_library(
            papers=example_papers,
        )
        message = syslira_manager.sync_zotero_collection(collection_key="NI94JZZ5")
        if message:
            logger.info(f"Zotero collection synced: {message}")

        # papers_df should still have required columns after sync
        has_columns = set(self.paper_library.get_library_df().columns.to_list())
        requires_columns = set(UNION_COLUMNS)
        logger.info(f"Difference columns: {has_columns.symmetric_difference(requires_columns)}")
        self.assertTrue(has_columns.issubset(requires_columns))
        # papers_df should not be empty after sync
        self.assertTrue(self.paper_library.get_library_df().empty is False)
        self.assertTrue(message)


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
