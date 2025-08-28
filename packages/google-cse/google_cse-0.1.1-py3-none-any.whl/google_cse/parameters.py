from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class SearchParameters(BaseModel):
    """Base parameters for Google Custom Search API."""

    c2coff: Literal["0", "1"] = Field(
        default="0",
        description="Enables/disables Simplified and Traditional Chinese Search"
    )
    country: Optional[str] = Field(
        default=None,
        description="Restricts search to documents from a particular country (e.g., 'US')"
    )
    date_restrict: Optional[str] = Field(
        default=None,
        description="Date restriction (e.g., 'd10', 'w2', 'm3', 'y1')"
    )
    exact_terms: Optional[str] = Field(
        default=None,
        description="Phrase that all documents must contain"
    )
    exclude_terms: Optional[str] = Field(
        default=None,
        description="Words or phrases that should not appear in results"
    )
    file_type: Optional[str] = Field(
        default=None,
        description="File extension filter (e.g., 'pdf', 'doc')"
    )
    filter: Literal["0", "1"] = Field(
        default="1",
        description="Duplicate content filter (1=on, 0=off)"
    )
    geolocation: Optional[str] = Field(
        default=None,
        description="Two-letter country code for user geolocation (e.g., 'US')"
    )
    high_range: Optional[str] = Field(
        default=None,
        description="Ending value for search range (used with low_range)"
    )
    language: Optional[str] = Field(
        default=None,
        description="User interface language (e.g., 'en', 'es')"
    )
    hq: Optional[str] = Field(
        default=None,
        description="Additional query terms with logical AND"
    )
    link_site: Optional[str] = Field(
        default=None,
        description="URL that all results should link to"
    )
    low_range: Optional[str] = Field(
        default=None,
        description="Starting value for search range (used with high_range)"
    )
    language_restrict: Optional[str] = Field(
        default=None,
        description="Language restriction (e.g., 'lang_en')"
    )
    or_terms: Optional[str] = Field(
        default=None,
        description="Additional search terms (at least one must be present)"
    )
    rights: Optional[str] = Field(
        default=None,
        description="Licensing filter (e.g., 'cc_publicdomain')"
    )
    safe: Literal["active", "off"] = Field(
        default="off",
        description="SafeSearch setting"
    )
    site_search: Optional[str] = Field(
        default=None,
        description="Site to include or exclude from results"
    )
    site_search_filter: Optional[Literal["e", "i"]] = Field(
        default=None,
        description="Include (i) or exclude (e) site_search results"
    )
    sort: Optional[str] = Field(
        default=None,
        description="Sort expression (e.g., 'date')"
    )
    start: Optional[int] = Field(
        default=None,
        ge=1,
        description="Index of first result (for pagination)"
    )
    num_results: Optional[int] = Field(
        default=None,
        description="Number of results to return (1-10)"
    )

    @field_validator("num_results")
    def validate_num_results(cls, v):
        if v is not None and not (1 <= v <= 10):
            raise ValueError("num_results must be between 1 and 10")
        return v


class WebSearchParameters(SearchParameters):
    """Parameters specific to web search."""
    pass


class ImageSearchParameters(SearchParameters):
    """Parameters specific to image search."""

    img_color_type: Optional[Literal["color", "gray", "mono", "trans"]] = Field(
        default=None,
        description="Image color type filter"
    )
    img_dominant_color: Optional[Literal[
        "black", "blue", "brown", "gray", "green", "orange",
        "pink", "purple", "red", "teal", "white", "yellow"
    ]] = Field(
        default=None,
        description="Dominant color filter for images"
    )
    img_size: Optional[Literal[
        "huge", "icon", "large", "medium", "small", "xlarge", "xxlarge"
    ]] = Field(
        default=None,
        description="Image size filter"
    )
    img_type: Optional[Literal[
        "clipart", "face", "lineart", "stock", "photo", "animated"
    ]] = Field(
        default=None,
        description="Image type filter"
    )