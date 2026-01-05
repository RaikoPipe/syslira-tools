import os
from typing import Dict, List, Optional

from pyzotero import zotero


class ZoteroClient:
    """Client for handling Zotero API operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        library_id: Optional[str] = None,
        library_type: str = "user",
    ):
        """
        Initialize Zotero client attributes.

        Args:
            api_key: The API key for the Zotero API.
            library_id: The library ID for the Zotero library.
            library_type: The type of library (user or group).
        """
        self.api_key = api_key or os.environ.get("ZOTERO_API_KEY")
        self.library_id = library_id or os.environ.get("ZOTERO_LIBRARY_ID")
        self.library_type = library_type
        self.client = None

        self.collections = {}

    def init(self, reinit: bool = False) -> str:
        """
        Initialize the Zotero API client.

        Args:
            reinit: Whether to reinitialize the client if it is already initialized.

        Returns:
            str: Message indicating the client has been initialized.
        """
        if self.client and not reinit:
            return "Zotero client already initialized."

        if not self.api_key:
            raise ValueError("API key is required to initialize the Zotero client.")

        if not self.library_id:
            raise ValueError("Library ID is required to initialize the Zotero client.")

        # Validate library type
        if self.library_type not in ["user", "group"]:
            raise ValueError("library_type must be 'user' or 'group'")

        self.client = zotero.Zotero(
            library_id=self.library_id,
            library_type=self.library_type,
            api_key=self.api_key,
        )

        return "Zotero client initialized."

    def get_all_items(self, collection_key: Optional[str] = None):
        """Get all items in the Zotero library."""
        if collection_key:
            return self.client.everything(self.client.collection_items_top(collection_key))
        return self.client.everything(self.client.top())

    def get_item(self, item_key: str):
        """Get a specific item from Zotero by key."""
        return self.client.item(item_key)

    def get_collection_items(self, collection_key: str):
        return self.client.collection_items(collection_key)

    def search_items(self, query: str):
        """Search for items in Zotero by query."""
        return self.client.items(q=query)

    def create_items(self, templates: List[Dict]):
        """Create new items in Zotero."""
        return self.client.create_items(templates)

    def update_item(self, template: Dict):
        """Update an existing item in Zotero."""
        return self.client.update_item(template)

    def item_template(self, itemtype: str):
        """Get an item template from Zotero."""
        return self.client.item_template(itemtype=itemtype)

    def check_items(self, templates: List[Dict]):
        """Check if templates are valid for Zotero."""
        return self.client.check_items(templates)

    def add_to_collection(self, collection_key: str, item):
        """Add an item to a Zotero collection."""
        return self.client.addto_collection(collection_key, item)

    def get_children(self, item_key: str):
        """Get children of a Zotero item (e.g., attachments)."""
        return self.client.children(item_key)

    def get_fulltext(self, item_key: str):
        """Get fulltext of a Zotero item."""
        return self.client.fulltext_item(item_key)

    def create_new_collections(self, collections: list[dict[str, str]]):
        """Create a new collection in Zotero."""
        return self.client.create_collection(collections)

    def get_file(self, item_key: str) -> bytes:
        """Get a file attachment from a Zotero item."""
        return self.client.file(item_key)