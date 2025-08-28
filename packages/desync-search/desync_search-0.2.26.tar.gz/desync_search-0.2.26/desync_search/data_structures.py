import json

class PageData:
    """
    Represents a single search result or page record, 
    corresponding to a row in the 'page_data' table.
    """

    def __init__(
        self,
        id=None,
        url="",
        domain="",
        timestamp="",
        bulk_search_id="",
        api_key_used="",
        search_type="",
        text_content="",
        html_content="",
        internal_links=None,
        external_links=None,
        latency_ms=None,
        complete=None,
        created_at=""
    ):
        self.id = id
        self.url = url
        self.domain = domain
        self.timestamp = timestamp
        self.bulk_search_id = bulk_search_id
        self.api_key_used = api_key_used
        self.search_type = search_type
        self.text_content = text_content
        self.html_content = html_content
        self.internal_links = internal_links or []
        self.external_links = external_links or []
        self.latency_ms = latency_ms
        self.complete = complete
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict):
        """
        Builds a PageData instance from a dict that 
        contains some/all fields from the 'page_data' schema.
        """
        return cls(
            id=data.get("id"),
            url=data.get("url", ""),
            domain=data.get("domain", ""),
            timestamp=data.get("timestamp", ""),
            bulk_search_id=data.get("bulk_search_id", ""),
            api_key_used=data.get("api_key", data.get("api_key_used", "")),  
            search_type=data.get("search_type", ""),
            text_content=data.get("text_content", ""),
            html_content=data.get("html_content", ""),
            internal_links=data.get("internal_links", []),
            external_links=data.get("external_links", []),
            latency_ms=data.get("latency_ms"),
            complete=data.get("complete"),
            created_at=data.get("created_at", "")
        )

    def __repr__(self):
        return (
            f"<PageData "
            f"url={self.url} "
            f"search_type={self.search_type} "
            f"timestamp={self.timestamp} "
            f"complete={self.complete}>"
        )
