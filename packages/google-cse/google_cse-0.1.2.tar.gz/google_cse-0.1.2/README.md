# Google CSE

[![PyPI version](https://img.shields.io/pypi/v/google-cse.svg)](https://pypi.org/project/google-cse/)
[![Python versions](https://img.shields.io/pypi/pyversions/google-cse.svg)](https://pypi.org/project/google-cse/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Downloads](https://pepy.tech/badge/google-cse)](https://pepy.tech/project/google-cse)

A clean, **type-safe Python client** for the [Google Custom Search JSON API](https://developers.google.com/custom-search/v1/overview).
This wrapper provides simple methods for **web** and **image** searches, with full type safety powered by **Pydantic models**.

---

## 🔧 Installation

```bash
pip install google-cse
```

---

## 🚀 Quick Start

```python
from google_cse import GoogleCSE, WebSearchParameters, ImageSearchParameters

# Initialize client
client = GoogleCSE(api_key="YOUR_API_KEY", search_engine_id="YOUR_SEARCH_ENGINE_ID")

# Web search
results = client.web_search("OpenAI GPT-5", num_results=5)
for r in results:
    print(r.title, "-", r.link)

# Image search
images = client.image_search("puppies", num_results=3)
for img in images:
    print(img.title, "-", img.link)
```

---

## 📦 Features

* ✅ Simple and clean API for Google Custom Search Engine
* ✅ Type-safe with [Pydantic models](https://docs.pydantic.dev/)
* ✅ Supports **web search** and **image search**
* ✅ Easy-to-use parameters for advanced queries

---

## ⚙️ API Reference

### `GoogleCSE(api_key: str, search_engine_id: str)`

Create a client for Google Custom Search.

* **api\_key** → Your Google API key
* **search\_engine\_id** → Your Programmable Search Engine ID

---

### Methods

#### 🔍 `web_search(query: str, start_index: int = 1, num_results: int = 10, parameters: Optional[WebSearchParameters] = None) -> List[WebSearchResult]`

Perform a web search.
Returns a list of simplified `WebSearchResult` objects.

#### 🖼️ `image_search(query: str, start_index: int = 1, num_results: int = 10, parameters: Optional[ImageSearchParameters] = None) -> List[ImageSearchResult]`

Perform an image search.
Returns a list of simplified `ImageSearchResult` objects.

#### ⚡ `raw_search(query: str, start_index: int = 1, num_results: int = 10, search_type: Optional[Literal["image"]] = None, parameters: Optional[SearchParameters] = None) -> GoogleSearchResponse`

Perform a raw search and return the **full API response** (typed).

---

## 📋 Example with Parameters

```python
# Web search with filtering
params = WebSearchParameters(
    exact_terms="OpenAI",
    site_search="openai.com",
    safe="active"
)

results = client.web_search("GPT", num_results=5, parameters=params)
for r in results:
    print(r.title, "-", r.snippet)

# Image search with filters
img_params = ImageSearchParameters(
    img_size="large",
    img_type="clipart"
)

images = client.image_search("cat", num_results=3, parameters=img_params)
for img in images:
    print(img.title, "-", img.context_link)
```

---

## 🔑 Authentication

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/).
2. Create a **Programmable Search Engine (CSE)** at [programmablesearchengine.google.com](https://programmablesearchengine.google.com/).
3. Enable **Custom Search API** in your project.
4. Pass your credentials to the client:

```python
client = GoogleCSE(api_key="YOUR_API_KEY", search_engine_id="YOUR_SEARCH_ENGINE_ID")
```

---

## ⚠️ Notes

* `num_results` must be between **1 and 10** (Google API limit).
* `start_index + num_results` must not exceed **100**.
* The package raises Python exceptions on network or API errors.

---

## 📜 License

Apache License 2.0 © 2025
