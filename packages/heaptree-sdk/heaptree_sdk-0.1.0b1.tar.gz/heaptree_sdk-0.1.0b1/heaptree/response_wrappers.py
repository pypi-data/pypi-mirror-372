"""
Result classes for Heaptree API responses.
"""


class CreateNodeResponseWrapper:
    def __init__(self, raw_response):
        self._raw = raw_response
    
    @property
    def node_id(self) -> str:
        """Convenience property for accessing single node ID when only one node was created."""
        node_ids = self._raw["node_ids"]
        if len(node_ids) == 1:
            return node_ids[0]
        elif len(node_ids) == 0:
            raise ValueError("No nodes were created")
        else:
            raise ValueError(
                f"Multiple nodes created ({len(node_ids)}). "
                f"Use .node_ids to access all node IDs: {node_ids}"
            )
    
    @property
    def web_access_url(self) -> str:
        """Convenience property for accessing single web access URL when only one node was created."""
        node_ids = self._raw["node_ids"]
        if len(node_ids) == 1:
            return self._raw["web_access_urls"][node_ids[0]]
        elif len(node_ids) == 0:
            raise ValueError("No nodes were created")
        else:
            raise ValueError(
                f"Multiple nodes created ({len(node_ids)}). "
                f"Use .web_access_urls to access all web access URLs: {self._raw['web_access_urls']}"
            )
    
    @property
    def node_ids(self) -> list[str]:
        return self._raw["node_ids"]
    
    @property
    def web_access_urls(self) -> dict[str, str]:
        return self._raw["web_access_urls"] 