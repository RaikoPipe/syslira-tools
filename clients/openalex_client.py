import os
from typing import Any, Dict, List, Optional
import pyalex
from pyalex import Works, Authors
import time


class OpenAlexClient:
    """Client for interacting with the OpenAlex API via pyalex."""

    def __init__(self, email: Optional[str] = None):
        """
        Initialize the OpenAlex client.

        Args:
            email: Email to identify your API requests (polite pool).
        """
        self.initialized = False
        self.email = email if email else os.environ.get("OPENALEX_EMAIL")

    def init(self) -> str:
        """Initialize the OpenAlex client with the provided credentials."""
        if not self.initialized:
            if self.email:
                pyalex.config.email = self.email  # Puts you in the polite pool :)
            self.initialized = True

        return "OpenAlex client initialized."

    def get_papers_count(
        self, query: dict, filter_args: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Get the total number of papers matching a search query.

        Args:
            query: The search query.
            filter_args: Additional filters to apply to the search.

        Returns:
            Total number of papers matching the search query.
        """
        self.init()
        result = (
            Works()
            .search_filter(**query)
            .filter(**filter_args if filter_args is not None else {})  # Apply any additional filters
            .count()  # Get the count of results
        )
        return result

    def search_papers(
        self,
        query: dict,
        limit: int = None,
        filter_args: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for papers on OpenAlex, collecting all results.

        Args:
            query: The search query.
            limit: Maximum number of papers to return (default: None for all results).
            filter_args: Additional filters to apply to the search.

        Returns:
            List of paper objects from OpenAlex.
        """
        self.init()

        page = 1
        per_page = 200  # Maximum allowed by the API
        all_results = []

        while True:
            # Make the API request with the current page
            results = (
                Works()
                .search_filter(**query)
                .filter(**filter_args if filter_args is not None else {})  # Apply any additional filters
                .get(page=page, per_page=per_page)
            )

            # if 429 error, wait and retry
            if (
                results
                and "status_code" in results
                and results["status_code"] == 429
                or page % 10 == 0
            ):
                time.sleep(1)
                continue

            # If no results or empty list, we've reached the end
            if not results:
                break

            # Add the current page results to our collection
            all_results.extend(results)

            # Check if we've reached the maximum requested
            if limit and len(all_results) >= limit:
                all_results = all_results[:limit]  # Trim to exact limit
                break

            # Check if we've retrieved all available results
            if len(results) < per_page:
                break

            # Move to the next page
            page += 1

        return all_results

    def get_paper_by_doi(self, doi: str) -> Dict[str, Any]:
        """
        Get a paper by DOI from OpenAlex.

        Args:
            doi: The DOI of the paper.

        Returns:
            Paper object from OpenAlex.
        """
        self.init()
        work = Works()[f"https://doi.org/{doi}"]
        return work

    def get_author_works(self, author_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get works by a specific author.

        Args:
            author_id: The OpenAlex ID of the author.
            limit: Maximum number of papers to return (default: 25).

        Returns:
            List of paper objects from OpenAlex.
        """
        self.init()
        works = Works().filter(author=author_id).get(per_page=limit)
        return works

    def search_authors(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search for authors on OpenAlex.

        Args:
            query: The search query.
            limit: Maximum number of authors to return (default: 25).

        Returns:
            List of author objects from OpenAlex.
        """
        self.init()
        authors = Authors().search(query).get(per_page=limit)
        return authors

    def get_related_works(self, work_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get works related to a specific work.

        Args:
            work_id: The OpenAlex ID of the work.
            limit: Maximum number of papers to return (default: 10).

        Returns:
            List of related paper objects from OpenAlex.
        """
        self.init()
        work = Works()[work_id]
        related_works = Works().filter(related_to=work_id).get(per_page=limit)
        return related_works

    def get_cited_by(self, work_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get works that cite a specific work.

        Args:
            work_id: The OpenAlex ID of the work.
            limit: Maximum number of papers to return (default: 25).

        Returns:
            List of paper objects from OpenAlex that cite the specified work.
        """
        self.init()
        cited_by = Works().filter(cites=work_id).get(per_page=limit)
        return cited_by

    @staticmethod
    def extract_eid_from_openalex(work: Dict[str, Any]) -> str:
        """
        Extract an EID-like identifier from OpenAlex work.

        Args:
            work: OpenAlex work object.

        Returns:
            A string identifier in EID format or empty string if not possible.
        """
        # OpenAlex doesn't have Scopus EIDs, so we create a pseudo-EID
        # using the OpenAlex ID which looks like: https://openalex.org/W2741809807
        if "id" in work and work["id"]:
            # Extract the ID part (W2741809807) and create a pseudo-EID
            alex_id = work["id"].split("/")[-1]
            return f"ALEX-{alex_id}"
        return ""
