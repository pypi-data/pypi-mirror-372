import logging
import requests
from typing import Optional, Dict, Any, List

from .parameters import *
from .results import *


class GoogleCSE:
    """
    A clean, type-safe client for Google Custom Search Engine API.

    This client provides a simple interface to perform web and image searches
    using Google's Custom Search JSON API with full type safety via Pydantic models.
    """

    BASE_URL = "https://customsearch.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize the Google CSE client.

        Args:
            api_key: Your Google API key
            search_engine_id: Your Programmable Search Engine ID
        """
        self._log = logging.getLogger(self.__class__.__name__)

        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def raw_search(
        self,
        query: str,
        start_index: int = 1,
        num_results: int = 10,
        search_type: Optional[Literal['image']] = None,
        parameters: Optional[SearchParameters] = None
    ) -> GoogleSearchResponse:
        """
        Perform a raw search query returning full API response.

        Args:
            query: The search query string
            num_results: Number of results to return (1-10)
            search_type: Type of search ("image" for image search, None for web)
            parameters: Search parameters object

        Returns:
            Dictionary containing full API response or None if error occurred
        """
        if start_index < 1:
            raise ValueError("start_index must start from 1")

        if not (1 <= num_results <= 10):
            raise ValueError("num_results must be between 1 and 10")

        if (start_index + num_results - 1) > 100:
            raise ValueError("because of google JSON API policy, the sum of start_index and num_results must not exceed 100")

        params = self._build_params(query, num_results, search_type, parameters)

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            search_response = GoogleSearchResponse.from_dict(response.json())
            return search_response

        except requests.exceptions.RequestException as e:
            self._log.error(f"Search request failed: {e}")
            raise

    def web_search(
        self,
        query: str,
        start_index: int = 1,
        num_results: int = 10,
        parameters: Optional[WebSearchParameters] = None
    ) -> List[WebSearchResult]:
        """
        Perform a web search and return simplified results.

        Args:
            query: Search query
            start_index: Number for starting index of result
            num_results: Number of results (1-10)
            parameters: Web search parameters

        Returns:
            List of WebSearchResult objects
        """
        results = self.raw_search(
            query=query,
            start_index=start_index,
            num_results=num_results,
            search_type=None,
            parameters=parameters
        )

        if results.items is None or len(results.items) == 0:
            return []

        web_results = [WebSearchResult.from_result(item) for item in results.items]
        return web_results

    def image_search(
        self,
        query: str,
        start_index: int = 1,
        num_results: int = 10,
        parameters: Optional[ImageSearchParameters] = None
    ) -> List[ImageSearchResult]:
        """
        Perform an image search and return simplified results.

        Args:
            query: Search query
            start_index: Number for starting index of result
            num_results: Number of results (1-10)
            parameters: Image search parameters

        Returns:
            List of ImageSearchResult objects
        """
        results = self.raw_search(
            query=query,
            start_index=start_index,
            num_results=num_results,
            search_type="image",
            parameters=parameters
        )

        if results.items is None or len(results.items) == 0:
            return []

        image_results = [ImageSearchResult.from_result(item) for item in results.items]
        return image_results

    def _build_params(
        self,
        query: str,
        num_results: int,
        search_type: Optional[Literal['image']],
        parameters: Optional[SearchParameters]
    ) -> Dict[str, Any]:
        """Build the parameters dictionary for the API request."""
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": num_results,
        }

        if search_type:
            if search_type not in ['image']:
                raise ValueError("search_type must be 'image' or None")

            params["searchType"] = search_type

        if parameters:
            # Map Pydantic model fields to API parameters
            field_mapping = {
                "c2coff": "c2coff",
                "country": "cr",
                "date_restrict": "dateRestrict",
                "exact_terms": "exactTerms",
                "exclude_terms": "excludeTerms",
                "file_type": "fileType",
                "filter": "filter",
                "geolocation": "gl",
                "high_range": "highRange",
                "language": "hl",
                "hq": "hq",
                "link_site": "linkSite",
                "low_range": "lowRange",
                "language_restrict": "lr",
                "or_terms": "orTerms",
                "rights": "rights",
                "safe": "safe",
                "site_search": "siteSearch",
                "site_search_filter": "siteSearchFilter",
                "sort": "sort",
                "start": "start",
                # Image-specific parameters
                "img_color_type": "imgColorType",
                "img_dominant_color": "imgDominantColor",
                "img_size": "imgSize",
                "img_type": "imgType",
            }

            for field_name, api_name in field_mapping.items():
                value = getattr(parameters, field_name, None)
                if value is not None:
                    params[api_name] = value

        return params