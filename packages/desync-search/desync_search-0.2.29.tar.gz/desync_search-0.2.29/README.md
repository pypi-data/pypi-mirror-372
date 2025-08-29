# Desync Search Documentation

---

## Overview

Desync Search is a next-generation Python library engineered for fast, stealthy, and scalable web data extraction. It combines low-detectability techniques, massive concurrency, and ease of integration to deliver the best performance and pricing in the market.

**Key Features:**

- **Stealth Mode:**  
  Operates with minimal detection, even on pages protected against bot traffic.

- **Massive Concurrency:**  
  Supports up to 50,000 concurrent operations, with any additional requests automatically queued.

- **Minimal Integration:**  
  Start using Desync Search in just three lines of code:
  ```python
  import desync_search
  client = desync_search.DesyncClient(user_api_key="YOUR_API_KEY")
  result = client.search("https://example.com")
  ```

- **Best-in-Class Pricing:**  
  Enjoy highly competitive pricing that offers exceptional value for high-volume operations.

- **Low Latency:**  
  Experience quick response times and efficient data extraction with consistently low latency.

---

## Installation & Setup

### 1. Installing the Library

To install Desync Search via pip, run:

```bash
pip install desync_search
```

### 2. Setting Up Your API Key

Desync Search uses your API key to authenticate requests. The `DesyncClient` automatically checks for an environment variable named `DESYNC_API_KEY` if you don't pass the key directly. This ensures secure and convenient usage.

#### Setting the Environment Variable

- **Unix/Linux/MacOS (bash):**
  ```bash
  export DESYNC_API_KEY="your_api_key_here"
  ```
- **Windows (Command Prompt):**
  ```cmd
  set DESYNC_API_KEY=your_api_key_here
  ```
- **Windows (PowerShell):**
  ```powershell
  $env:DESYNC_API_KEY="your_api_key_here"
  ```

### 3. Initializing the Client

Once your API key is set, you can initialize the client without specifying the API key:

```python
from desync_search import DesyncClient

client = DesyncClient()
```

Alternatively, you can pass a different API key directly:

```python
client = DesyncClient(user_api_key="your_api_key_here")
```

---

## Quickstart

Below are ready-to-run code examples that demonstrate the core features of Desync Search. Simply copy these snippets into your IDE, update your API key if necessary (or set it in your environment), and run!

### 1. Performing a Single Search

**What It Does:**  
Searches a single URL and returns detailed page data—including the URL, links, and content length—packaged in a `PageData` object.

```python
from desync_search import DesyncClient

client = DesyncClient()
target_url = "https://example.com"
result = client.search(target_url)

print("URL:", result.url)
print("Internal Links:", len(result.internal_links))
print("External Links:", len(result.external_links))
print("Text Content Length:", len(result.text_content))
```

---

### 2. Crawling an Entire Domain

**What It Does:**  
Recursively crawls a website. The starting page is considered "depth 0". Any link on that page (pointing to the same domain) is considered "depth 1", links from those pages are "depth 2", and so on. This continues until the maximum depth is reached or no new unique pages are found.

```python
from desync_search import DesyncClient

client = DesyncClient()

pages = client.crawl(
    start_url="https://example.com",
    max_depth=2,
    scrape_full_html=False,
    remove_link_duplicates=True
)

print(f"Discovered {len(pages)} pages.")
for page in pages:
    print("URL:", page.url, "| Depth:", getattr(page, "depth", "N/A"))
```

---

### 3. Initiating a Bulk Search

**What It Does:**  
Processes a list of URLs asynchronously in one operation. Up to 1000 URLs can be processed per bulk search. This method returns metadata including a unique bulk search ID that you can later use to retrieve the complete results.

```python
from desync_search import DesyncClient

client = DesyncClient()
urls = [
    "https://example.com",
    "https://another-example.com",
    # Add additional URLs here (up to 1000 per bulk search)
]

bulk_info = client.bulk_search(target_list=urls, extract_html=False)
print("Bulk Search ID:", bulk_info.get("bulk_search_id"))
print("Total Links Scheduled:", bulk_info.get("total_links"))
```

*Note:* Once you have the `bulk_search_id`, you can retrieve the results asynchronously using the `collect_results` method. For a fully managed experience, consider using `simple_bulk_search`.

---

### 4. Collecting Bulk Search Results

**What It Does:**  
After initiating a bulk search, this snippet polls for and collects the complete results. The method waits until a specified fraction of the URLs have been processed (or a timeout is reached) and then retrieves the full page data.

```python
from desync_search import DesyncClient

client = DesyncClient()
urls = [
    "https://example.com",
    "https://another-example.com",
    # Add more URLs as needed
]

# Initiate a bulk search
bulk_info = client.bulk_search(target_list=urls, extract_html=False)

# Poll and collect results once enough pages are complete
results = client.collect_results(
    bulk_search_id=bulk_info["bulk_search_id"],
    target_links=urls,
    wait_time=30.0,
    poll_interval=2.0,
    completion_fraction=0.975
)

print(f"Retrieved {len(results)} pages from the bulk search.")
for result in results:
    print("URL:", result.url)
```

---

### 5. Using Simple Bulk Search

**What It Does:**  
For large lists of URLs (even exceeding 1000 elements), the `simple_bulk_search` method splits the list into manageable chunks, starts a bulk search for each chunk, and then aggregates all the results. This provides a fully managed bulk search experience.

```python
from desync_search import DesyncClient

client = DesyncClient()
urls = [
    "https://example.com",
    "https://another-example.com",
    # Add as many URLs as needed; this method handles splitting automatically.
]

results = client.simple_bulk_search(
    target_list=urls,
    extract_html=False,
    poll_interval=2.0,
    wait_time=30.0,
    completion_fraction=1
)

print(f"Retrieved {len(results)} pages using simple_bulk_search.")
for result in results:
    print("URL:", result.url)
```

---

## API Reference

### DesyncClient Class

The `DesyncClient` class provides a high-level interface to the Desync Search API, managing individual searches, bulk operations, domain crawling, and credit balance checks.

#### `__init__(user_api_key="", developer_mode=False)`
**Signature:**
```python
def __init__(self, user_api_key="", developer_mode=False)
```
**Description:**  
Initializes the client with the provided API key or reads it from the `DESYNC_API_KEY` environment variable. If `developer_mode` is `True`, the client uses a test endpoint; otherwise, it uses the production endpoint.

**Parameters:**
- `user_api_key` *(str, optional)*: Your Desync API key.
- `developer_mode` *(bool, optional)*: Toggle between test and production endpoints.

**Example:**
```python
from desync_search import DesyncClient

client = DesyncClient(user_api_key="YOUR_API_KEY", developer_mode=False)
```

---

#### `search(url, search_type="stealth_search", scrape_full_html=False, remove_link_duplicates=True) -> PageData`
**Signature:**
```python
def search(self, url, search_type="stealth_search", scrape_full_html=False, remove_link_duplicates=True) -> PageData
```
**Description:**  
Performs a single search on a specified URL and returns a `PageData` object containing the page’s text, links, timestamps, and other metadata.

**Parameters:**
- `url` *(str)*: The URL to scrape.
- `search_type` *(str)*: Either `"stealth_search"` (default) or `"test_search"`.
- `scrape_full_html` *(bool)*: If `True`, returns the full HTML content.
- `remove_link_duplicates` *(bool)*: If `True`, removes duplicate links from the results.

**Example:**
```python
result = client.search("https://example.com")
print(result.text_content)
```

---

#### `bulk_search(target_list, extract_html=False) -> dict`
**Signature:**
```python
def bulk_search(self, target_list, extract_html=False) -> dict
```
**Description:**  
Initiates an asynchronous bulk search on up to 1000 URLs at once. Returns a dictionary containing a `bulk_search_id` and other metadata.

**Parameters:**
- `target_list` *(list[str])*: List of URLs to process.
- `extract_html` *(bool)*: If `True`, includes the full HTML content in results.

**Example:**
```python
bulk_info = client.bulk_search(target_list=["https://example.com", "https://another-example.net"])
print(bulk_info["bulk_search_id"])
```

---

#### `list_available(url_list=None, bulk_search_id=None) -> list`
**Signature:**
```python
def list_available(self, url_list=None, bulk_search_id=None) -> list
```
**Description:**  
Retrieves minimal data about previously collected search results (IDs, domains, timestamps, etc.). Returns a list of `PageData` objects with limited fields.

**Parameters:**
- `url_list` *(list[str], optional)*: Filters results by specific URLs.
- `bulk_search_id` *(str, optional)*: Filters results by a particular bulk search ID.

**Example:**
```python
partial_records = client.list_available(bulk_search_id="some-bulk-id")
for rec in partial_records:
    print(rec.url, rec.complete)
```

---

#### `pull_data(record_id=None, url=None, domain=None, timestamp=None, bulk_search_id=None, search_type=None, latency_ms=None, complete=None, created_at=None) -> list`
**Signature:**
```python
def pull_data(self, record_id=None, url=None, domain=None, timestamp=None, bulk_search_id=None, search_type=None, latency_ms=None, complete=None, created_at=None) -> list
```
**Description:**  
Retrieves full data (including text and optional HTML content) for one or more records matching the provided filters. Returns a list of `PageData` objects.

**Example:**
```python
detailed_records = client.pull_data(url="https://example.com")
for record in detailed_records:
    print(record.html_content)
```

---

#### `pull_credits_balance() -> dict`
**Signature:**
```python
def pull_credits_balance(self) -> dict
```
**Description:**  
Checks the user’s current credit balance and returns it as a dictionary.

**Example:**
```python
balance_info = client.pull_credits_balance()
print(balance_info["credits_balance"])
```

---

#### `collect_results(bulk_search_id: str, target_links: list, wait_time=30.0, poll_interval=2.0, completion_fraction=0.975) -> list`
**Signature:**
```python
def collect_results(self, bulk_search_id: str, target_links: list, wait_time=30.0, poll_interval=2.0, completion_fraction=0.975) -> list
```
**Description:**  
Polls periodically for bulk search completion until a specified fraction of pages are done or a maximum wait time elapses, then retrieves full data. Returns a list of `PageData` objects.

**Parameters:**
- `bulk_search_id` *(str)*: The unique identifier for the bulk search.
- `target_links` *(list[str])*: The list of URLs in the bulk job.
- `wait_time` *(float)*: Maximum polling duration in seconds.
- `poll_interval` *(float)*: Interval between status checks.
- `completion_fraction` *(float)*: Fraction of completed results needed to stop polling.

**Example:**
```python
results = client.collect_results(
    bulk_search_id="bulk-id-123",
    target_links=["https://example.com", "https://another.com"]
)
print(len(results))
```

---

#### `simple_bulk_search(target_list: list, extract_html=False, poll_interval=2.0, wait_time=30.0, completion_fraction=1) -> list`
**Signature:**
```python
def simple_bulk_search(self, target_list: list, extract_html=False, poll_interval=2.0, wait_time=30.0, completion_fraction=1) -> list
```
**Description:**  
Splits a large list of URLs into chunks (up to 1000 URLs each), initiates a bulk search for each chunk, then collects and aggregates the results.

**Example:**
```python
all_pages = client.simple_bulk_search(
    target_list=["https://site1.com", "https://site2.com", ...],
    extract_html=False
)
print(len(all_pages))
```

---

#### `crawl(start_url: str, max_depth=2, scrape_full_html=False, remove_link_duplicates=True, poll_interval=2.0, wait_time_per_depth=30.0, completion_fraction=0.975) -> list`
**Signature:**
```python
def crawl(self, start_url: str, max_depth=2, scrape_full_html=False, remove_link_duplicates=True, poll_interval=2.0, wait_time_per_depth=30.0, completion_fraction=0.975) -> list
```
**Description:**  
Recursively crawls the specified `start_url` up to `max_depth` levels. It performs a stealth search on the starting page, collects same-domain links, and uses bulk searches to fetch pages at each depth.  
*Think of it this way: the starting page is "depth 0". Any same-domain link on that page is "depth 1", links on depth 1 pages become "depth 2", and so on until the maximum depth is reached or no new pages are found.*

**Example:**
```python
crawled_pages = client.crawl(
    start_url="https://example.com",
    max_depth=3,
    scrape_full_html=False
)
print(len(crawled_pages))
```

---

#### `_post_and_parse(payload)`
**Signature:**
```python
def _post_and_parse(self, payload)
```
**Description:**  
An internal helper method that sends the given payload to the API, parses the JSON response, and raises an error if the request fails.

---

### PageData Class

The `PageData` class packages all the information extracted from a web page during a search. It includes both details about the page itself and metadata about the search operation (such as timestamps and latency).

#### Attributes

- **`id` (int):**  
  A unique identifier for the search result.

- **`url` (str):**  
  The URL targeted by the search, often referred to as the "target URL" or "target page" (e.g., `abc.com/news`).

- **`domain` (str):**  
  The domain of the targeted URL (e.g., if the URL is `abc.com/news`, the domain is `abc.com`).

- **`timestamp` (int):**  
  A Unix timestamp marking when the result was received.

- **`bulk_search_id` (str):**  
  A unique identifier for the bulk search batch this result belongs to. May be `NONE` if not part of a bulk search.

- **`search_type` (str):**  
  Indicates the type of search performed. Options include:
  - **`stealth_search`** (default): Uses JavaScript rendering and stealth techniques.
  - **`test_search`**: Does not render JavaScript; intended for prototyping.

- **`text_content` (str):**  
  The text extracted from the page’s DOM, ideal for data extraction.

- **`html_content` (str):**  
  The full HTML content of the page (optional and not returned by default to save bandwidth).

- **`internal_links` (list[str]):**  
  A list of URLs on the page that point to the same domain.

- **`external_links` (list[str]):**  
  A list of URLs on the page that point to different domains.

- **`latency_ms` (int):**  
  The time in milliseconds between the start of the search and when the results were collected.

- **`complete` (bool):**  
  Indicates whether the search operation is complete.

- **`created_at` (int):**  
  A Unix timestamp marking when the search was initiated on the client-side.

---

This documentation provides you with everything you need to get started with Desync Search—from installation and quickstart examples to detailed API reference for both the client and the page data structure. Enjoy building your web data extraction projects!
```