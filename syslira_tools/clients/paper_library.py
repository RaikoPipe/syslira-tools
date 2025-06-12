from pandas import notna
from typing import Any, Dict, List, Union, Optional

import pandas as pd

from const import UNION_COLUMNS, ITEMTYPE_MAP
from syslira_tools.clients.zotero_client import ZoteroClient
from syslira_tools.clients.openalex_client import OpenAlexClient
from syslira_tools.helpers.obj_util import getattr_or_empty_str
from syslira_tools.helpers.conversion import convert_inverted_index
from loguru import logger


class PaperLibrary:
    """Manager for the paper library with local storage, Zotero and OpenAlex integration."""

    def __init__(
        self,
        #scopus_client: ScopusClient,
        zotero_client: ZoteroClient,
        openalex_client: OpenAlexClient,  # Add OpenAlex client
        collection_key: str = None,
    ):
        """
        Initialize the paper library manager.

        Args:
            scopus_client: Initialized ScopusClient instance.
            zotero_client: Initialized ZoteroClient instance.
            openalex_client: Initialized OpenAlexClient instance (optional).
            collection_key: Default working collection key for Zotero.
        """
        #self.scopus_client = scopus_client
        self.zotero_client = zotero_client
        self.openalex_client = openalex_client
        self.columns = list(UNION_COLUMNS)
        self.papers_df = pd.DataFrame(columns=self.columns, dtype=str)
        self.papers_df.set_index("id", inplace=True)
        self.collection_key = collection_key

    def get_library_df(self):
        """Return the paper library pandas dataframe"""
        return self.papers_df

    # def get_count_search_results_scopus(self, query: str) -> str:
    #     """
    #     Get the number of search results from Scopus.
    #
    #     Args:
    #         query: The search query.
    #
    #     Returns:
    #         Number of results.
    #     """
    #     self.scopus_client.init()
    #
    #     try:
    #         count = self.scopus_client.get_results_size(query)
    #     except Exception as e:
    #         return f"Error retrieving number of results: {e}"
    #
    #     return f"Number of results for query '{query}': {count}"
    #
    # def add_papers_from_scopus(
    #     self, query: str
    # ) -> Union[str, tuple[List[Dict[str, Any]], str]]:
    #     """
    #     Search for papers on Scopus and add to the library.
    #
    #     Args:
    #         query: The search query.
    #
    #     Returns:
    #         Result and status message.
    #     """
    #     # Initialize Scopus if not already
    #     self.scopus_client.init()
    #
    #     duplicates = []
    #     added_papers = []
    #
    #     try:
    #         papers = self.scopus_client.search_papers(query=query)
    #     except Exception as e:
    #         return f"Error searching for papers: {e}"
    #
    #     if not papers:
    #         return "No papers found for the query"
    #
    #     papers_details = self._create_library_items(papers, source="scopus")
    #
    #     # Add the papers to the library if they are not already there
    #     for paper in copy(papers_details):
    #         if paper["eid"] in self.papers_df.index:
    #             duplicates.append(paper["title"])
    #             papers_details.remove(paper)
    #         else:
    #             added_papers.append(paper["title"])
    #
    #     if papers_details:
    #         paper_details_df = pd.DataFrame(
    #             papers_details, index=[paper["eid"] for paper in papers_details]
    #         )
    #         self.papers_df = pd.concat([self.papers_df, paper_details_df])
    #
    #     return (
    #         f"Added {len(papers_details)} papers to the library; "
    #         f"{len(duplicates)} duplicates were found. "
    #     )

    def get_count_search_results(
        self, query: dict, limit: int = 25, filter_args: Optional[dict] = None
    ) -> str:
        """
        Search openalex for papers and return the number of results.

        Args:
            query: The search query.
            limit: Maximum number of papers to return.
            filter_args: Additional filter arguments for OpenAlex search.

        Returns:
            Result and status message.
        """

        # Initialize OpenAlex if not already
        self.openalex_client.init()

        try:
            count = self.openalex_client.get_papers_count(
                query=query, filter_args=filter_args
            )
        except Exception as e:
            return f"Error searching for papers on OpenAlex: {e}"

        if not count:
            return "No papers found for the query on OpenAlex"

        return f"Number of results for query '{query}': {count}"

    def retrieve_papers(
        self, query: dict, limit: int = 25, filter_args: Optional[dict] = None
    ) -> str | list[dict[str, Any]]:
        """
        Search for papers on OpenAlex and return.

        Args:
            query: The search query.
            limit: Maximum number of papers to return.
            filter_args: Additional filter arguments for OpenAlex search.

        Returns:
            Result and status message.
        """
        # Initialize OpenAlex if not already
        self.openalex_client.init()

        try:
            papers = self.openalex_client.search_papers(
                query=query, limit=limit, filter_args=filter_args
            )
            if not papers:
                return "No papers found for the query on OpenAlex"
            return papers
        except Exception as e:
            return f"Error searching for papers on OpenAlex: {e}"

    def add_papers_to_library(
            self, papers: List[Any]
    ) -> str:
        """
        Add papers to the library.

        Args:
            papers: List of paper objects from openalex

        Returns:
            Result and status message.
        """

        if papers:
            papers_details = self._create_library_items(papers, source="openalex")
            return self.update_library(papers_details)
        else:
            raise ValueError("No papers provided to add to the library.")


    def update_library(self, papers: List[Any]) -> str:
        # Create DataFrame from new papers
        paper_details_df = pd.DataFrame(
            papers, index=[paper["id"] for paper in papers]
        )

        # Deduplication step (more efficient than two separate calls)
        paper_details_df = paper_details_df.drop_duplicates(subset=["title"])
        paper_details_df = paper_details_df.drop_duplicates(subset=["DOI"])

        # Get initial counts before merge
        initial_count = len(self.papers_df)
        new_papers_count = len(paper_details_df)

        # Combine and deduplicate in one step
        combined_df = pd.concat([self.papers_df, paper_details_df]).drop_duplicates(
            subset=["title", "DOI"], keep="last"
        )

        # Calculate metrics
        final_count = len(combined_df)
        num_added = final_count - initial_count
        num_duplicates = new_papers_count - num_added

        self.papers_df = combined_df

        return (
            f"Added {num_added} papers from OpenAlex to the library; "
            f"{num_duplicates} existing were found and updated."
        )

    # def add_papers_by_doi(
    #     self, doi_list: List[str]
    # ) -> Union[str, tuple[List[Dict[str, Any]], str]]:
    #     """
    #     Add papers to the library by their DOIs using OpenAlex.
    #
    #     Args:
    #         doi_list: List of DOIs to fetch.
    #
    #     Returns:
    #         Result and status message.
    #     """
    #     if not self.openalex_client:
    #         return "OpenAlex client not initialized. Please initialize it first."
    #
    #     # Initialize OpenAlex if not already
    #     self.openalex_client.init()
    #
    #     duplicates = []
    #     added_papers = []
    #     not_found = []
    #     papers_details = []
    #
    #     for doi in doi_list:
    #         try:
    #             paper = self.openalex_client.get_paper_by_doi(doi)
    #             if not paper:
    #                 not_found.append(doi)
    #                 continue
    #
    #             # Convert the single paper to a list for _create_library_items
    #             paper_details = self._create_library_items([paper], source="openalex")
    #
    #             if not paper_details:
    #                 not_found.append(doi)
    #                 continue
    #
    #             # Use the single item from the list
    #             paper_detail = paper_details[0]
    #
    #             if paper_detail["eid"] in self.papers_df.index:
    #                 duplicates.append(paper_detail["title"])
    #             else:
    #                 papers_details.append(paper_detail)
    #                 added_papers.append(paper_detail["title"])
    #
    #         except Exception as e:
    #             not_found.append(doi)
    #             logger.error(f"Error fetching paper with DOI {doi} from OpenAlex: {e}")
    #
    #     if papers_details:
    #         paper_details_df = pd.DataFrame(
    #             papers_details, index=[paper["eid"] for paper in papers_details]
    #         )
    #         self.papers_df = pd.concat([self.papers_df, paper_details_df])
    #
    #     return (
    #         f"Added {len(added_papers)} papers from OpenAlex to the library; "
    #         f"{len(duplicates)} duplicates were found. "
    #         f"{len(not_found)} DOIs could not be found: {not_found}"
    #     )
    #
    # def add_papers_by_author(
    #     self, author_query: str, limit: int = 25
    # ) -> Union[str, tuple[List[Dict[str, Any]], str]]:
    #     """
    #     Add papers by a specific author to the library using OpenAlex.
    #
    #     Args:
    #         author_query: Author name or identifier to search for.
    #         limit: Maximum number of papers to return.
    #
    #     Returns:
    #         Result and status message.
    #     """
    #     if not self.openalex_client:
    #         return "OpenAlex client not initialized. Please initialize it first."
    #
    #     # Initialize OpenAlex if not already
    #     self.openalex_client.init()
    #
    #     # First, search for the author
    #     try:
    #         authors = self.openalex_client.search_authors(author_query, limit=5)
    #     except Exception as e:
    #         return f"Error searching for author on OpenAlex: {e}"
    #
    #     if not authors:
    #         return f"No authors found for the query: {author_query}"
    #
    #     # Use the first author found
    #     author = authors[0]
    #     author_id = author["id"]
    #     author_name = author.get("display_name", "Unknown Author")
    #
    #     # Get works by this author
    #     try:
    #         papers = self.openalex_client.get_author_works(author_id, limit=limit)
    #     except Exception as e:
    #         return (
    #             f"Error retrieving papers for author {author_name} from OpenAlex: {e}"
    #         )
    #
    #     if not papers:
    #         return f"No papers found for author: {author_name}"
    #
    #     # Process and add the papers
    #     papers_details = self._create_library_items(papers, source="openalex")
    #
    #     # Add the papers to the library if they are not already there
    #     duplicates = []
    #     added_papers = []
    #
    #     for paper in copy(papers_details):
    #         if paper["eid"] in self.papers_df.index:
    #             duplicates.append(paper["title"])
    #             papers_details.remove(paper)
    #         else:
    #             added_papers.append(paper["title"])
    #
    #     if papers_details:
    #         paper_details_df = pd.DataFrame(
    #             papers_details, index=[paper["eid"] for paper in papers_details]
    #         )
    #         self.papers_df = pd.concat([self.papers_df, paper_details_df])
    #
    #     return (
    #         f"Added {len(papers_details)} papers by author {author_name} to the library; "
    #         f"{len(duplicates)} duplicates were found. "
    #     )

    # def find_related_papers(
    #     self, paper_eid: str, limit: int = 10
    # ) -> Union[str, tuple[List[Dict[str, Any]], str]]:
    #     """
    #     Find papers related to a paper in the library using OpenAlex.
    #
    #     Args:
    #         paper_eid: The EID of the paper in the library.
    #         limit: Maximum number of related papers to return.
    #
    #     Returns:
    #         Result and status message.
    #     """
    #     if not self.openalex_client:
    #         return "OpenAlex client not initialized. Please initialize it first."
    #
    #     # Check if the paper exists in the library
    #     if paper_eid not in self.papers_df.index:
    #         return f"Paper with EID {paper_eid} not found in library."
    #
    #     # Get the paper details
    #     paper = self.papers_df.loc[paper_eid]
    #
    #     # Check if the paper has an OpenAlex ID (typically stored in the eid field for OpenAlex papers)
    #     if not paper_eid.startswith("ALEX-"):
    #         # Try to find it by DOI if available
    #         if pd.notna(paper.get("DOI")) and paper.get("DOI"):
    #             try:
    #                 alex_paper = self.openalex_client.get_paper_by_doi(paper["DOI"])
    #                 if not alex_paper:
    #                     return (
    #                         f"Could not find paper with DOI {paper['DOI']} in OpenAlex."
    #                     )
    #                 work_id = alex_paper["id"]
    #             except Exception as e:
    #                 return f"Error finding paper in OpenAlex: {e}"
    #         else:
    #             return "Paper does not have an OpenAlex ID or DOI. Cannot find related papers."
    #     else:
    #         # Extract OpenAlex ID from the pseudo-EID (ALEX-W12345 → W12345)
    #         work_id = paper_eid.replace("ALEX-", "")
    #
    #         # Add full URL format if needed
    #         if not work_id.startswith("https://"):
    #             work_id = f"https://openalex.org/{work_id}"
    #
    #     # Find related papers
    #     try:
    #         related_papers = self.openalex_client.get_related_works(
    #             work_id, limit=limit
    #         )
    #     except Exception as e:
    #         return f"Error finding related papers: {e}"
    #
    #     if not related_papers:
    #         return f"No related papers found for paper {paper.get('title', paper_eid)}"
    #
    #     # Process and add the related papers
    #     papers_details = self._create_library_items(related_papers, source="openalex")
    #
    #     # Add the papers to the library if they are not already there
    #     duplicates = []
    #     added_papers = []
    #
    #     for paper in copy(papers_details):
    #         if paper["eid"] in self.papers_df.index:
    #             duplicates.append(paper["title"])
    #             papers_details.remove(paper)
    #         else:
    #             added_papers.append(paper["title"])
    #
    #     if papers_details:
    #         paper_details_df = pd.DataFrame(
    #             papers_details, index=[paper["eid"] for paper in papers_details]
    #         )
    #         self.papers_df = pd.concat([self.papers_df, paper_details_df])
    #
    #     return (
    #         f"Added {len(papers_details)} related papers to the library; "
    #         f"{len(duplicates)} related papers were already in the library. "
    #     )

    def _create_library_items(
        self, papers: List[Any], source: str = "scopus"
    ) -> List[Dict[str, Any]]:
        """
        Extract details from the list of papers.

        Args:
            papers: List of paper objects (from Scopus or OpenAlex).
            source: Source of the papers ('scopus' or 'openalex').

        Returns:
            list: List of dictionaries containing paper details.
        """
        papers_details = []

        # Use appropriate extraction method based on source
        if source == "scopus":
            return self._extract_scopus_papers(papers)
        elif source == "openalex":
            return self._extract_openalex_papers(papers)
        else:
            raise ValueError(f"Unknown source: {source}")

    @staticmethod
    def _extract_scopus_papers(papers: List[Any]) -> List[Dict[str, Any]]:
        """
        Extract details from the list of Scopus papers.

        Args:
            papers: List of Scopus paper objects.

        Returns:
            list: List of dictionaries containing paper details.
        """
        papers_details = []
        for paper in papers:
            try:
                # Need to extract the Scopus ID from the EID
                scopus_id = paper.eid.split("-")[-1]

                # Create a dictionary with the main paper details
                paper_details = {
                    "title": getattr_or_empty_str(paper, "title"),
                    "date": getattr_or_empty_str(paper, "coverDate"),
                    "volume": getattr_or_empty_str(paper, "volume"),
                    "DOI": getattr_or_empty_str(paper, "doi"),
                    "pages": getattr_or_empty_str(paper, "pageRange"),
                }

                # extract authors
                if getattr_or_empty_str(paper, "author_names"):
                    for author_name in paper.author_names:
                        last_name, first_name = author_name.split(", ", 1)
                        paper_details["creator"] = [
                            {
                                "creatorType": "author",
                                "firstName": first_name,
                                "lastName": last_name,
                            }
                        ]
                else:
                    last_name, first_name = paper.creator.split(" ", 1)
                    paper_details["creators"] = [
                        {
                            "creatorType": "author",
                            "firstName": first_name,
                            "lastName": last_name,
                        }
                    ]

                # Check if subtype is considered
                if paper.subtype not in ITEMTYPE_MAP:
                    raise ValueError(f"Paper subtype {paper.subtype} not supported.")
                paper_details["itemType"] = ITEMTYPE_MAP[paper.subtype]

                # add conference paper exclusive fields
                if paper.subtype == "cp":
                    paper_details["proceedingsTitle"] = getattr_or_empty_str(
                        paper, "publicationName"
                    )
                    paper_details["conferenceName"] = getattr_or_empty_str(
                        paper, "conferenceName"
                    )
                    affiliation_city = getattr_or_empty_str(paper, "affiliation_city")
                    affiliation_country = getattr_or_empty_str(
                        paper, "affiliation_country"
                    )
                    paper_details["place"] = (
                        f"{affiliation_city}, {affiliation_country}"
                    )

                else:
                    # paper assumed as journal article
                    paper_details["publicationTitle"] = getattr_or_empty_str(
                        paper, "publicationName"
                    )
                    paper_details["issue"] = getattr_or_empty_str(
                        paper, "article_number"
                    )

                # add extra columns
                paper_details["eid"] = getattr_or_empty_str(paper, "eid")
                paper_details["scopusId"] = getattr_or_empty_str(paper, "scopus_id")
                paper_details["description"] = getattr_or_empty_str(
                    paper, "description"
                )
                paper_details["citedByCount"] = getattr_or_empty_str(
                    paper, "citedby_count"
                )
                paper_details["collections"] = []
                paper_details["source"] = "scopus"
                paper_details["tags"] = []
                paper_details["relations"] = {}

                papers_details.append(paper_details)
            except Exception as e:
                logger.error(
                    f"Error retrieving details for Scopus paper {getattr_or_empty_str(paper, 'title')}: {e}"
                )
                continue

        return papers_details

    def _extract_openalex_papers(
        self, papers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract details from the list of OpenAlex papers.

        Args:
            papers: List of OpenAlex paper objects.

        Returns:
            list: List of dictionaries containing paper details.
        """
        papers_details = []
        for paper in papers:
            try:
                # Create a dictionary with the main paper details
                paper_details = {
                    "title": paper.get("title", ""),
                    "date": paper.get("publication_date", ""),
                    "volume": paper.get("volume", ""),
                    "DOI": paper.get("doi", "").replace("https://doi.org/", ""),
                    "pages": f"{paper.get('first_page', '')}-{paper.get('last_page', '')}",
                    "itemType": "journalArticle",  # Default
                }

                # Extract authors
                creators = []
                if paper.get("authorships"):
                    for authorship in paper["authorships"]:
                        author = authorship.get("author", {})
                        name = author.get("display_name", "")
                        if name:
                            # Try to split name into first and last
                            name_parts = name.split()
                            if len(name_parts) > 1:
                                first_name = " ".join(name_parts[:-1])
                                last_name = name_parts[-1]
                            else:
                                first_name = ""
                                last_name = name

                            creators.append(
                                {
                                    "creatorType": "author",
                                    "firstName": first_name,
                                    "lastName": last_name,
                                }
                            )

                paper_details["creators"] = creators

                # Set publication information
                if paper.get("host_venue"):
                    venue = paper["host_venue"]
                    paper_details["publicationTitle"] = venue.get("display_name", "")

                    # Determine item type based on venue type
                    venue_type = venue.get("type", "").lower()
                    if venue_type == "journal":
                        paper_details["itemType"] = "journalArticle"
                    elif venue_type == "conference":
                        paper_details["itemType"] = "conferencePaper"
                        paper_details["proceedingsTitle"] = venue.get(
                            "display_name", ""
                        )
                    elif venue_type == "repository":
                        paper_details["itemType"] = "preprint"

                    # Add issue information
                    paper_details["issue"] = venue.get("issue", "")

                # Add citation count
                if paper.get("cited_by_count"):
                    paper_details["citedByCount"] = str(paper.get("cited_by_count", 0))

                # Add abstract
                if paper.get("abstract_inverted_index") and not paper.get("abstractNote"):
                    paper_details["abstractNote"] = convert_inverted_index(paper.get("abstract_inverted_index"))

                if paper.get("fulltext"):
                    paper_details["fulltext"] = paper.get("fulltext", "")
                else:
                    paper_details["fulltext"] = "" # Placeholder for fulltext

                # Create a pseudo-EID for OpenAlex items
                paper_details["id"] = paper.get("id", self.openalex_client.extract_eid_from_openalex(paper))

                paper_details["collections"] = []
                paper_details["tags"] = []
                paper_details["relations"] = {}

                papers_details.append(paper_details)
            except Exception as e:
                logger.error(
                    f"Error retrieving details for OpenAlex paper {paper.get('title', '')}: {e}"
                )
                continue

        return papers_details

    # def update_library_with_openalex_metadata(self):
    #     """
    #     Update the library with metadata from OpenAlex (for example, if scopus doesn't provide all metadata due to non-subscriber status)
    #
    #     Returns:
    #         str: Status message.
    #     """
    #     if not self.openalex_client:
    #         return "OpenAlex client not initialized. Please initialize it first."
    #
    #     # Initialize OpenAlex if not already
    #     self.openalex_client.init()
    #
    #     updated = []
    #     not_found = []
    #     papers_metadata_openalex = []
    #     for paper_id, paper in self.papers_df.iterrows():
    #         try:
    #             # Fetch metadata from OpenAlex
    #             metadata = self.openalex_client.get_paper_by_doi(paper["DOI"])
    #             if metadata:
    #                 papers_metadata_openalex.append(metadata)
    #             else:
    #                 not_found.append(paper["DOI"])
    #                 raise ValueError(
    #                     f"Paper with DOI {paper['DOI']} not found in OpenAlex."
    #                 )
    #
    #         except Exception as e:
    #             logger.error(f"Error updating paper {paper['title']} from OpenAlex: {e}")
    #
    #     # Process the papers
    #     papers_details = self._create_library_items(
    #         papers_metadata_openalex, source="openalex"
    #     )
    #
    #     # Update the library with the new metadata
    #     for paper in copy(papers_details):
    #         if paper["eid"] in self.papers_df.index:
    #             updated.append(paper["title"])
    #             # Update the existing paper with new metadata
    #             self.papers_df.loc[paper["eid"]] = paper
    #         else:
    #             not_found.append(paper["title"])
    #
    #     return f"Updated {len(updated)} papers with OpenAlex metadata."

    # Rest of the class methods remain unchanged
    def update_from_zotero(self) -> str:
        """
        Update the local library with papers from Zotero. Also retrieves full text if available.

        Returns:
            str: Status message.
        """
        # Initialize Zotero if not already
        self.zotero_client.init()

        zotero_items = self.zotero_client.get_all_items(
            collection_key=self.collection_key
        )
        added = []
        updated = []

        for item in zotero_items:
            # create new item
            item["data"]["zoteroKey"] = item["key"]
            item["data"]["id"] = (
                item["data"]["extra"]
                if getattr_or_empty_str(item, "extra") != ""
                else item["key"]
            )  # use zotero key if id was never given

            # download full text
            try:
                fulltext = self.retrieve_fulltext_from_zotero_item(item["key"])
                item["data"]["fulltext"] = fulltext["content"]
            except Exception as e:
                logger.debug(f"Could not retrieve fulltext for item {item['key']}: {e}")

            if item["data"]["title"] not in self.papers_df["title"].values:
                added.append(item)
            else:
                # item already exists
                paper = self.papers_df.loc[self.papers_df["title"] == item["data"]["title"]] # existing paper
                item["data"]["id"] = paper.index[0]  # use existing id
                updated.append(item)
        if added or updated:
            return self.update_library(added + updated)
        # todo: change return string
        return f"Added {len(added)} papers from Zotero to local library. Updated {len(updated)} existing papers."

    def update_zotero_from_library(
        self, update_existing: bool = False
    ) -> str:
        """
        Update the Zotero library with the papers in the local library.

        Args:
            update_existing: Whether to update existing items in Zotero.

        Returns:
            str: Status message.
        """
        # Initialize Zotero if not already
        self.zotero_client.init()

        added_titles = []
        updated_titles = []
        skipped_titles = []
        error_titles = []
        errors = []

        collection_items = self.zotero_client.get_collection_items(self.collection_key)

        for paper_id, paper in self.papers_df.iterrows():
            try:
                result_status = self._add_item_to_zotero(
                    paper_id, paper, self.collection_key, collection_items, update_existing
                )
                if result_status == "added":
                    added_titles.append(paper.title)
                elif result_status == "updated":
                    updated_titles.append(paper.title)
                else:
                    skipped_titles.append(paper.title)

            except Exception as e:
                logger.warning(f"Error adding paper {paper['title']} to Zotero: {e}")
                error_titles.append(paper.title)
                errors.append(str(e))

        return (
            f"Added {len(added_titles)} papers to Zotero library. "
            f"Updated {len(updated_titles)} existing papers. "
            f"Skipped {len(skipped_titles)} papers. "
            f"{len(error_titles)} errors occurred. "
        )

    def sync_zotero_collection(
        self, update_existing: bool = False
    ) -> str:
        """
        Synchronize both the local library and Zotero collection.

        Args:
            update_existing: Whether to update existing items in Zotero.

        Returns:
            str: Status message.
        """
        # Initialize Zotero if not already
        self.zotero_client.init()

        # update local library
        local_update = self.update_from_Zotero()

        zotero_update = self.update_zotero_from_library(update_existing)

        return (
            f"Zotero -> Local library \n\n: {local_update} "
            f"Local library -> Zotero \n\n: {zotero_update}"
        )

    def _add_item_to_zotero(
        self, paper_id:str, paper: pd.Series, collection_key: str, collection_items: Optional[List[Dict]] = None, update_existing=False,
    ) -> str:
        """
        Add a paper item to Zotero.

        Args:
            paper: The paper details as a pandas Series.
            collection_key: The key of the collection to add the paper to.
            update_existing: Whether to update the item if it already exists in Zotero.

        Returns:
            str: Status message (added, updated, or skipped).
        """
        # Check if item already exists
        existing_item = None
        collection_key = collection_key if collection_key else self.collection_key

        if notna(paper.get("zoteroKey")):
            # Check if item is already in zotero
            try:
                # fixme: there has to be a better way to compare to existing collection items
                if collection_items:
                    existing_item = next(
                        (item for item in collection_items if item["key"] == paper["zoteroKey"]),
                        None,
                    )
                else:
                    existing_item = self.zotero_client.get_item(paper["zoteroKey"])
            except Exception as e:
                existing_item = None

        if not existing_item:
            # Check if in zotero by title
            found_titles = self.zotero_client.search_items(paper.title)

            if found_titles:
                existing_item = found_titles[0]
                # Update paper in library with zotero key
                self.papers_df.loc[paper_id, "zoteroKey"] = existing_item["key"]

        if existing_item and update_existing:
            template = self._create_zotero_item(paper_id, collection_key, paper)
            result = self.zotero_client.update_item(existing_item["key"], template)
            return "updated"
        elif existing_item:
            return "skipped"
        else:
            # Create new item in zotero
            zot_item = self._create_zotero_item(paper_id, collection_key, paper)
            try:
                result = self.zotero_client.create_items([zot_item])
            except Exception as e:
                raise Exception(f"Error creating item in Zotero: {e}")

            if not result.get("successful"):
                raise Exception(f"Error creating item in Zotero: {result['failed']}")

            # Update the zotero key in the papers library
            self.papers_df.loc[paper_id, "zoteroKey"] = result["successful"]["0"][
                "key"
            ]

            # Add to collection if specified
            if collection_key and "successful" in result and result["successful"]:
                # Get the key of the first successfully created item
                self.zotero_client.add_to_collection(
                    collection_key, result["successful"]["0"]
                )

            return "added"

    def _create_zotero_item(self, paper_id: str, collection_key: str, paper: pd.Series) -> Dict:
        """
        Create a Zotero item template from paper data.

        Args:
            collection_key: The key of the collection to add the paper to.
            paper: The paper details as a pandas Series.

        Returns:
            dict: Zotero item template.
        """
        collection_key = collection_key if collection_key else self.collection_key
        template = self.zotero_client.item_template(itemtype=paper.itemType)

        # fill template fields with paper data
        for field in template.keys():
            template[field] = getattr_or_empty_str(paper, field)
        template["extra"] = paper_id

        if collection_key:
            template["collections"] = [collection_key]

        checked_item = self.zotero_client.check_items([template])

        return checked_item[0]

    def get_attachment_info(self, item_key: str) -> Dict:
        """
        Retrieve information about attachments for a Zotero item.

        Args:
            item_key: The key of the Zotero item to retrieve attachments for.

        Returns:
            dict: Information about the attachments.
        """
        # Initialize Zotero if not already
        self.zotero_client.init()

        # Get the item
        item = self.zotero_client.get_item(item_key)

        # Get the children of the item (i.e., attachments)
        children = self.zotero_client.get_children(item_key)

        # Extract information about the attachments
        attachments = []
        for child in children:
            content_type = child["data"].get("contentType")
            key = child["data"].get("key")
            if key and content_type:
                attachment = {
                    "key": key,
                    "contentType": content_type,
                    # optional attributes
                    "title": child["data"]["title"] if hasattr(child["data"], "title") else None,
                    "linkMode": child["data"]["linkMode"] if hasattr(child["data"], "linkMode") else None,
                    "url": child["data"]["url"] if hasattr(child["data"], "url") else None,
                }
                attachments.append(attachment)


        return {"item": item, "attachments": attachments}

    def retrieve_all_zotero_attachments(self) -> str:
        # Initialize Zotero if not already
        self.zotero_client.init()

        downloaded = []
        errors = []

        for paper_id, paper in self.papers_df.iterrows():
            if paper["zoteroKey"]:
                try:
                    fulltext = self.retrieve_fulltext_from_zotero_item(paper["zoteroKey"])
                    self.papers_fulltext_df.at[paper.index, "fulltext"] = fulltext
                    downloaded.append(paper["title"])
                except Exception as e:
                    errors.append(paper["title"])
                    logger.debug(f"Could not download file for paper {paper['title']}: {e}")

        return (
            f"Downloaded {len(downloaded)} files. "
            f"{len(errors)} errors occurred. "
            f"\n Downloaded: {downloaded} "
            f"\n Errors: {errors}"
        )

    def retrieve_fulltext_from_zotero_item(self, item_key: str) -> Dict:
        """
        Retrieve full-text content for a Zotero item and store in library. Will raise exception if
        no attachment was found.

        Args:
            item_key: The key of the Zotero item.

        Returns:
            dict: Full-text content and metadata.
        """
        attachments = self.get_attachment_info(item_key).get("attachments")

        if attachments:
            # Get first attachment that is a PDF
            pdf_attachments = [
                x for x in attachments if x.get("contentType") == "application/pdf"
            ]

            if not pdf_attachments:
                raise Exception("No PDF attachments found for item.")

            target_attachment = pdf_attachments[0]
            try:
                return self.zotero_client.get_fulltext(target_attachment["key"])
            except Exception:
                raise Exception(
                    f"Valid attachment with key {target_attachment['key']} was found, but no fulltext could be retrieved. A potential workaround is to re-retrieve the fulltext through the Zotero client UI."
                )
        else:
            raise Exception("No attachments found for item.")


    def get_paper_text(self, paper_id: str, text_type: str = "fulltext") -> str:
        """
        Retrieve the full-text content for a paper in the library.

        Args:
            paper_id: The ID of the paper.
            text_type: The type of text to retrieve (fulltext or abstract).

        Returns:
            str: Requested text content.
        """

        if text_type not in ["fulltext", "abstractNote"]:
            raise ValueError("text_type must be either 'fulltext' or 'abstractNote'.")

        if paper_id in self.papers_df.index:
            try:
                text = self.papers_df.at[paper_id, text_type]
                if isinstance(text, str) and text != "":
                    return text
                raise ValueError(
                    f"{text_type} content not available for paper with ID {paper_id}. Consider downloading it first through Zotero UI client."
                )
            except Exception as e:
                logger.error(
                    f"Error retrieving {text_type} for paper with ID {paper_id}: {e}"
                )
                raise ValueError(
                    f"Error retrieving {text_type} for paper with ID {paper_id}: {e}"
                )
        else:
            raise ValueError(f"Paper with ID {paper_id} not found in library.")


    def set_paper_tags(self, paper_id: str, tags: List[str]) -> str:
        """
        Set tags for a paper in the library.

        Args:
            paper_id: The ID of the paper.
            tags: List of tags to set for the paper.

        Returns:
            str: Status message.
        """
        if paper_id in self.papers_df.index:
            self.papers_df.loc[paper_id, "tags"] = tags
            return f"Tags {tags} set for paper with ID {paper_id}."
        else:
            raise ValueError(f"Paper with ID {paper_id} not found in library.")

    def add_paper_summary(self, paper_id: str, summary: str) -> str:
        """
        Add a summary to a paper in the library.

        Args:
            paper_id: The ID of the paper.
            summary: The summary to add to the paper.

        Returns:
            str: Status message.
        """
        if paper_id in self.papers_df.index:
            self.papers_df.loc[paper_id, "summary"] = summary
            return f"Summary added for paper with ID {paper_id}."
        else:
            raise ValueError(f"Paper with ID {paper_id} not found in library.")

    def export_library_to_csv(self, file_path: str) -> str:
        """
        Export the library to a CSV file.

        Args:
            file_path: The path to save the CSV file.

        Returns:
            str: Status message.
        """
        try:
            self.papers_df.to_csv(file_path, index=True)
            return f"Library exported to {file_path}."
        except Exception as e:
            logger.error(f"Error exporting library to CSV: {e}")
            raise ValueError(f"Error exporting library to CSV: {e}")