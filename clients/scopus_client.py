import os
from typing import Optional

import pybliometrics.scopus
from pybliometrics.scopus import ScopusSearch


class ScopusClient:
    """Client for handling Scopus API operations."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Scopus client.

        Args:
            api_key: The API key for the Elsevier API.
        """
        self.api_key = api_key or os.environ.get("ELSEVIER_API_KEY")
        self.initialized = False

    def init(self, reinit: bool = False) -> str:
        """
        Initialize the Scopus/pybliometrics API.

        Args:
            reinit: Whether to reinitialize the client if it is already initialized.

        Returns:
            str: Message indicating the client has been initialized.
        """
        if self.initialized and not reinit:
            return "Scopus client already initialized."
        pybliometrics.scopus.create_config(keys=[self.api_key])
        pybliometrics.scopus.init(keys=[self.api_key])
        self.initialized = True

        if self.api_key:
            return "Client initialized with API key set."

        return "Client initialized without API key set. API access may be limited."

    def search_papers(self, query: str) -> list:
        """
        Search for papers on Scopus based on a keyword query.

        Args:
            query: The search query.

        Returns:
            list: List of scopus paper objects
        """
        if not self.initialized:
            raise Exception("Scopus client not initialized. Please run init() first.")

        # Execute the search with pybliometrics
        search = ScopusSearch(
            query,
            subscriber=False,
            download=True,
        )
        return search.results

    def get_results_size(self, query: str) -> int:
        """
        Get the number of results for a given query.

        Args:
            query: The search query.

        Returns:
            int: Number of results for the query.
        """
        if not self.initialized:
            raise Exception("Scopus client not initialized. Please run init() first.")

        # Execute the search with pybliometrics
        search = ScopusSearch(
            query,
            subscriber=False,
            download=False,
        )
        return search.get_results_size()
