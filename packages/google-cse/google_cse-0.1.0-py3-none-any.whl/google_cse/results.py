from typing import List, Optional
from pydantic import BaseModel, Field


class PromotionBodyLine(BaseModel):
    title: Optional[str] = Field(default=None)
    html_title: Optional[str] = Field(default=None, alias="htmlTitle")
    url: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "PromotionBodyLine":
        return PromotionBodyLine.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class PromotionImage(BaseModel):
    source: Optional[str] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "PromotionImage":
        return PromotionImage.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class Promotion(BaseModel):
    title: Optional[str] = Field(default=None)
    html_title: Optional[str] = Field(default=None, alias="htmlTitle")
    link: Optional[str] = Field(default=None)
    display_link: Optional[str] = Field(default=None, alias="displayLink")
    body_lines: Optional[List[PromotionBodyLine]] = Field(default=None, alias="bodyLines")
    image: Optional[PromotionImage] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "Promotion":
        return Promotion.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class ImageInfo(BaseModel):
    context_link: Optional[str] = Field(default=None, alias="contextLink")
    height: Optional[int] = Field(default=None)
    width: Optional[int] = Field(default=None)
    byte_size: Optional[int] = Field(default=None, alias="byteSize")
    thumbnail_link: Optional[str] = Field(default=None, alias="thumbnailLink")
    thumbnail_height: Optional[int] = Field(default=None, alias="thumbnailHeight")
    thumbnail_width: Optional[int] = Field(default=None, alias="thumbnailWidth")

    @staticmethod
    def from_dict(data: dict) -> "ImageInfo":
        return ImageInfo.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class LabelInfo(BaseModel):
    name: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None, alias="displayName")
    label_with_op: Optional[str] = Field(default=None, alias="label_with_op")

    @staticmethod
    def from_dict(data: dict) -> "LabelInfo":
        return LabelInfo.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class Result(BaseModel):
    kind: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    html_title: Optional[str] = Field(default=None, alias="htmlTitle")
    link: Optional[str] = Field(default=None)
    display_link: Optional[str] = Field(default=None, alias="displayLink")
    snippet: Optional[str] = Field(default=None)
    html_snippet: Optional[str] = Field(default=None, alias="htmlSnippet")
    cache_id: Optional[str] = Field(default=None, alias="cacheId")
    formatted_url: Optional[str] = Field(default=None, alias="formattedUrl")
    html_formatted_url: Optional[str] = Field(default=None, alias="htmlFormattedUrl")
    pagemap: Optional[dict] = Field(default=None)
    mime: Optional[str] = Field(default=None)
    file_format: Optional[str] = Field(default=None, alias="fileFormat")
    image: Optional[ImageInfo] = Field(default=None)
    labels: Optional[List[LabelInfo]] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "Result":
        return Result.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class QueryItem(BaseModel):
    title: Optional[str] = Field(default=None)
    total_results: Optional[str] = Field(default=None, alias="totalResults")
    search_terms: Optional[str] = Field(default=None, alias="searchTerms")
    count: Optional[int] = Field(default=None)
    start_index: Optional[int] = Field(default=None, alias="startIndex")
    start_page: Optional[int] = Field(default=None, alias="startPage")
    language: Optional[str] = Field(default=None)
    input_encoding: Optional[str] = Field(default=None, alias="inputEncoding")
    output_encoding: Optional[str] = Field(default=None, alias="outputEncoding")
    safe: Optional[str] = Field(default=None)
    cx: Optional[str] = Field(default=None)
    sort: Optional[str] = Field(default=None)
    filter: Optional[str] = Field(default=None)
    gl: Optional[str] = Field(default=None)
    cr: Optional[str] = Field(default=None)
    google_host: Optional[str] = Field(default=None, alias="googleHost")
    disable_cn_tw_translation: Optional[str] = Field(default=None, alias="disableCnTwTranslation")
    hq: Optional[str] = Field(default=None)
    hl: Optional[str] = Field(default=None)
    site_search: Optional[str] = Field(default=None, alias="siteSearch")
    site_search_filter: Optional[str] = Field(default=None, alias="siteSearchFilter")
    exact_terms: Optional[str] = Field(default=None, alias="exactTerms")
    exclude_terms: Optional[str] = Field(default=None, alias="excludeTerms")
    link_site: Optional[str] = Field(default=None, alias="linkSite")
    or_terms: Optional[str] = Field(default=None, alias="orTerms")
    related_site: Optional[str] = Field(default=None, alias="relatedSite")
    date_restrict: Optional[str] = Field(default=None, alias="dateRestrict")
    low_range: Optional[str] = Field(default=None, alias="lowRange")
    high_range: Optional[str] = Field(default=None, alias="highRange")
    file_type: Optional[str] = Field(default=None, alias="fileType")
    rights: Optional[str] = Field(default=None)
    search_type: Optional[str] = Field(default=None, alias="searchType")
    img_size: Optional[str] = Field(default=None, alias="imgSize")
    img_type: Optional[str] = Field(default=None, alias="imgType")
    img_color_type: Optional[str] = Field(default=None, alias="imgColorType")
    img_dominant_color: Optional[str] = Field(default=None, alias="imgDominantColor")

    @staticmethod
    def from_dict(data: dict) -> "QueryItem":
        return QueryItem.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class QuerySet(BaseModel):
    previous_page: Optional[List[QueryItem]] = Field(default=None, alias="previousPage")
    request: Optional[List[QueryItem]] = Field(default=None)
    next_page: Optional[List[QueryItem]] = Field(default=None, alias="nextPage")

    @staticmethod
    def from_dict(data: dict) -> "QuerySet":
        return QuerySet.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class UrlInfo(BaseModel):
    type: Optional[str] = Field(default=None)
    template: Optional[str] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "UrlInfo":
        return UrlInfo.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class SearchInformation(BaseModel):
    search_time: Optional[float] = Field(default=None, alias="searchTime")
    formatted_search_time: Optional[str] = Field(default=None, alias="formattedSearchTime")
    total_results: Optional[str] = Field(default=None, alias="totalResults")
    formatted_total_results: Optional[str] = Field(default=None, alias="formattedTotalResults")

    @staticmethod
    def from_dict(data: dict) -> "SearchInformation":
        return SearchInformation.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class SpellingInfo(BaseModel):
    corrected_query: Optional[str] = Field(default=None, alias="correctedQuery")
    html_corrected_query: Optional[str] = Field(default=None, alias="htmlCorrectedQuery")

    @staticmethod
    def from_dict(data: dict) -> "SpellingInfo":
        return SpellingInfo.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class GoogleSearchResponse(BaseModel):
    kind: Optional[str] = Field(default=None)
    url: Optional[UrlInfo] = Field(default=None)
    queries: Optional[QuerySet] = Field(default=None)
    promotions: Optional[List[Promotion]] = Field(default=None)
    context: Optional[dict] = Field(default=None)
    search_information: Optional[SearchInformation] = Field(default=None, alias="searchInformation")
    spelling: Optional[SpellingInfo] = Field(default=None)
    items: Optional[List[Result]] = Field(default=None)

    @staticmethod
    def from_dict(data: dict) -> "GoogleSearchResponse":
        return GoogleSearchResponse.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)

class WebSearchResult(BaseModel):
    title: Optional[str] = Field(default=None)
    html_title: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)
    display_link: Optional[str] = Field(default=None)
    snippet: Optional[str] = Field(default=None)
    html_snippet: Optional[str] = Field(default=None)
    formatted_url: Optional[str] = Field(default=None)

    @staticmethod
    def from_result(data: "Result") -> "WebSearchResult":
        return WebSearchResult(
            title=data.title,
            html_title=data.html_title,
            link=data.link,
            display_link=data.display_link,
            snippet=data.snippet,
            html_snippet=data.html_snippet,
            formatted_url=data.formatted_url,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class ImageSearchResult(BaseModel):
    title: Optional[str] = Field(default=None)
    html_title: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)
    display_link: Optional[str] = Field(default=None)
    snippet: Optional[str] = Field(default=None)
    context_link: Optional[str] = Field(default=None)
    image_height: Optional[int] = Field(default=None)
    image_width: Optional[int] = Field(default=None)
    image_byte_size: Optional[int] = Field(default=None)
    thumbnail_link: Optional[str] = Field(default=None)
    thumbnail_height: Optional[int] = Field(default=None)
    thumbnail_width: Optional[int] = Field(default=None)

    @staticmethod
    def from_result(data: "Result") -> "ImageSearchResult":
        image_data = data.image if data.image else None
        return ImageSearchResult(
            title=data.title,
            html_title=data.html_title,
            link=data.link,
            display_link=data.display_link,
            snippet=data.snippet,
            context_link=image_data.context_link if image_data else None,
            image_height=image_data.height if image_data else None,
            image_width=image_data.width if image_data else None,
            image_byte_size=image_data.byte_size if image_data else None,
            thumbnail_link=image_data.thumbnail_link if image_data else None,
            thumbnail_height=image_data.thumbnail_height if image_data else None,
            thumbnail_width=image_data.thumbnail_width if image_data else None,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)