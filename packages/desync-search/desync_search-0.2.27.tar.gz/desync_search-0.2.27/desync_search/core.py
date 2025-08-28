# File: desync_search/core.py

import requests
import json
import time
from desync_search.data_structures import PageData
import uuid
import math
from urllib.parse import urlparse
import os

API_VERSION = "v0.2.27"

def _split_into_equal_sub_lists(lst, max_size=1000):
    """
    Splits a list into N sub-lists, each of size as close as possible,
    ensuring no sub-list exceeds `max_size` in length.
    
    Example:
      - If `len(lst) = 1400` and `max_size=1000`, we'll produce 2 chunks of ~700 each.
      - If `len(lst) = 2300` and `max_size=1000`, we'll produce 3 chunks, each ~766/767 in size.
    """
    n = len(lst)
    if n <= max_size:
        return [lst]  # Only one sub-list needed
    
    # Number of chunks needed:
    number_of_chunks = math.ceil(n / float(max_size))
    # We'll make them as close to equal in size as possible
    chunk_size_floor = n // number_of_chunks
    remainder = n % number_of_chunks

    sublists = []
    start = 0
    for i in range(number_of_chunks):
        # Distribute remainder across the first 'remainder' chunks
        this_chunk_size = chunk_size_floor + (1 if i < remainder else 0)
        sublists.append(lst[start:start + this_chunk_size])
        start += this_chunk_size
    return sublists

class DesyncClient:
    """
    A high-level client for the Desync Search API.
    This handles search (stealth/test), retrieving previously collected search data,
    and pulling the user's credit balance.
    """

    def __init__(self, user_api_key="", developer_mode=False):
        """
        Initialize the client with a user_api_key.
        The base URL is fixed to the current production endpoint.
        """
        self.version = API_VERSION
        if user_api_key != "":
            self.user_api_key = user_api_key
        else:
            user_api_key = os.getenv("DESYNC_API_KEY")
            if user_api_key:
                self.user_api_key = user_api_key
            else:
                raise ValueError("You must provide a valid API key or store one in the evireoment as DESYNC_API_KEY")

        if developer_mode:
            self.base_url = "https://prku2ngdahnemmpibutatfr6zm0jazmb.lambda-url.us-east-1.on.aws/"
        else:
            self.base_url = "https://nycv5sx75joaxnzdkgvpx5mcme0butbo.lambda-url.us-east-1.on.aws/"


    def search(
        self,
        url,
        search_type="stealth_search",
        scrape_full_html=False,
        remove_link_duplicates=True
    ) -> PageData:
        """
        Performs a search. By default, does a 'stealth_search' (cost: 10 credits),
        but you can supply 'test_search' for a cheaper test operation (cost: 1 credit).

        :param url: The URL to scrape.
        :param search_type: Either "stealth_search" (default) or "test_search".
        :param scrape_full_html: If True, returns full HTML. Default False.
        :param remove_link_duplicates: If True, deduplicate discovered links. Default True.

        :return: A single PageData object representing the newly scraped page record.
                 Raises RuntimeError if the API returns success=False or on HTTP error.
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "search",
            "flags": {
                "search_type": search_type,
                "target_list": [url],
                "scrape_full_html": scrape_full_html,
                "remove_link_duplicates": remove_link_duplicates
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }
        resp = self._post_and_parse(payload)  # a dict with "data" inside
        # Typically: {"success": True, "data": {...}}
        data_dict = resp.get("data", {})
        return PageData.from_dict(data_dict)

    def bulk_search(
        self,
        target_list,
        extract_html=False
    ) -> dict:
        """
        Initiates a "bulk_search" operation on the Desync API, which:
        1) Checks if user_api_key has enough credits (10 credits/URL).
        2) Charges them in one shot.
        3) Invokes a Step Functions workflow to asynchronously handle all links.

        :param target_list: A list of URLs to process in this bulk search.
        :param bulk_search_id: An optional string to identify this bulk job.
        :param extract_html: If True, includes HTML in the scraper. Default False.

        :return: A dict with keys such as:
            {
            "message": "Bulk search triggered successfully.",
            "bulk_search_id": "...",
            "total_links": 25,
            "cost_charged": 250,
            "execution_arn": "arn:aws:states:..."
            }
        Raises RuntimeError if the API returns success=False or if there's an HTTP error.
        """
        if not isinstance(target_list, list) or len(target_list) == 0:
            raise ValueError("bulk_search requires a non-empty list of URLs.")
        elif len(target_list) > 1000:
            raise ValueError("bulk_search should not be passed more than 1000 links at the same time.")
        bulk_search_id = uuid.uuid4()
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "bulk_search",
            "flags": {
                "target_list": target_list,
                "bulk_search_id": str(bulk_search_id),
                "extract_html": extract_html
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }

        resp = self._post_and_parse(payload)  # e.g. { "success": True, "data": {...} }
        # 'resp["data"]' might look like:
        # {
        #   "message": "Bulk search triggered successfully.",
        #   "bulk_search_id": "...",
        #   "total_links": 25,
        #   "cost_charged": 250,
        #   "execution_arn": "arn:aws:states:..."
        # }

        data_dict = resp.get("data", {})
        data_dict["bulk_search_id"] = str(bulk_search_id)
        return data_dict

    def queue_scrape(self,
                     target_list,
                     *,
                     bulk_search_id=None,
                     search_type="crawler",
                     priority=0,
                     max_attempts=2,
                     timeout_sec=60.0,
                     poll_every_sec=0.5,
                     return_html=False,
                     html_truncate_bytes=200000) -> list:
        """
        Enqueue a list of URLs into the server-side Postgres queue and
        synchronously wait (up to timeout_sec) for results. Returns a list of
        PageData objects for whatever finished within the time budget. If all
        finish early, returns early.

        This mirrors your Lambda tester's contract.
        """
        if not isinstance(target_list, list) or not target_list:
            raise ValueError("queue_scrape requires a non-empty list of URLs.")

        bulk_search_id = str(bulk_search_id or uuid.uuid4())
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "queue_scrape",
            "flags": {
                "bulk_search_id": bulk_search_id,
                "search_type": search_type,
                "priority": int(priority),
                "max_attempts": int(max_attempts),
                "timeout_sec": float(timeout_sec),
                "poll_every_sec": float(poll_every_sec),
                "return_html": bool(return_html),
                "html_truncate_bytes": int(html_truncate_bytes) if html_truncate_bytes is not None else None,
                "target_list": target_list,
            },
            "metadata": {"api_version": API_VERSION}
        }

        # Give the HTTP call enough time (Lambda times out at 45/60s sometimes)
        http_timeout = max(float(timeout_sec) + 15.0, 30.0)
        resp = self._post_and_parse(payload, timeout=http_timeout)
        result = resp.get("data", {}) or {}

        # 'result' has 'results': [ {...page_data-like...}, ... ]
        rows = result.get("results", [])
        return [PageData.from_dict(r) for r in rows]

    def list_available(self, url_list=None, bulk_search_id=None) -> list:
        """
        Lists minimal data about previously collected search results (IDs, domain, timestamps, etc.).
        Returns a list of PageData objects (with limited fields).
        
        :param url_list: An optional list of URLs to filter by.
        :param bulk_search_id: An optional bulk search ID to filter by.
        :return: A list of PageData objects containing minimal record fields.
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": {
                "retrieval_type": "list_available"
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }

        # If the caller wants to filter by one or more URLs, pass that list along:
        if url_list is not None and isinstance(url_list, list) and len(url_list) > 0:
            payload["flags"]["url_list"] = url_list

        # If the caller wants to filter by bulk_search_id, pass it along:
        if bulk_search_id is not None:
            payload["flags"]["bulk_search_id"] = bulk_search_id

        resp = self._post_and_parse(payload)  # e.g. {"success": True, "data": [ {...}, {...} ]}
        data_list = resp.get("data", [])

        return [PageData.from_dict(item) for item in data_list]


    def pull_data(self, 
                  record_id=None, 
                  url=None, 
                  domain=None, 
                  timestamp=None, 
                  bulk_search_id=None, 
                  search_type=None, 
                  latency_ms=None, 
                  complete=None, 
                  created_at=None) -> list:
        """
        Pulls full data for one or more records (including text_content, html_content, etc.).
        :param record_id: Filter by specific record ID.
        :param url_filter: (Optional) If you want to filter by 'url' instead.
        :return: A list of PageData objects, in case multiple records match the filters.
        """
        flags = {
            "retrieval_type": "pull"
        }
        if record_id is not None:
            flags["id"] = record_id
        if url is not None:
            flags["url"] = url
        if domain is not None:
            flags["domain"] = domain
        if timestamp is not None:
            flags["timestamp"] = timestamp
        if bulk_search_id is not None:
            flags["bulk_search_id"] = bulk_search_id
        if search_type is not None:
            flags["search_type"] = search_type
        if latency_ms is not None:
            flags["latency_ms"] = latency_ms
        if complete is not None:
            flags["complete"] = complete
        if created_at is not None:
            flags["created_at"] = created_at

        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": flags,
            "metadata": {
                "api_version": API_VERSION
            }
        }
        resp = self._post_and_parse(payload)
        # resp["data"] is a list of dict
        data_list = resp.get("data", [])
        return [PageData.from_dict(d) for d in data_list]

    def pull_credits_balance(self) -> dict:
        """
        Checks the user's own credit balance.
        Returns a dict: e.g. {"success": True, "credits_balance": 240}
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": {
                "retrieval_type": "pull_credits_balance"
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }
        return self._post_and_parse(payload)  # e.g. { "success": True, "credits_balance": 240 }
    
    def collect_results(
        self,
        bulk_search_id: str,
        target_links: str,
        wait_time: float = 30.0,
        poll_interval: float = 2.0,
        completion_fraction: float = 0.975
    ) -> list:
        """
        Polls periodically until either the fraction of completed links 
        meets/exceeds `completion_fraction` OR we've waited `wait_time` seconds.
        
        Then, retrieves the full data for this bulk_search_id via `pull_data`.

        :param bulk_search_id: The ID for the bulk job to monitor.
        :param total_links:    The total number of URLs in that job.
        :param wait_time:      The maximum time (seconds) to poll before retrieving results. Default 30s.
        :param poll_interval:  How frequently (seconds) to poll `list_available`. Default 2s.
        :param completion_fraction: Fraction of completed links required 
                                    to stop polling early. Default 0.975 (97.5%).

        :return: A list of `PageData` objects (full data) from `pull_data(bulk_search_id=...)`.
        """
        start_time = time.time()
        total_links = len(target_links)
        # We'll track the fraction of 'complete' results
        while True:
            elapsed = time.time() - start_time
            if elapsed > wait_time:
                # We exceeded the max wait time -> break out and pull what we can
                break

            # 1) Poll minimal info about pages with this bulk_search_id
            partial_results = self.list_available(
                bulk_search_id=bulk_search_id
            )
            # 'partial_results' is a list of PageData with minimal fields, 
            # including `.complete` (True/False).

            # 2) Count how many are complete
            num_complete = sum(1 for page in partial_results if page.complete != False)
            fraction_complete = num_complete / float(total_links) if total_links > 0 else 1.0

            # 3) Check if fraction is enough
            if fraction_complete >= completion_fraction:
                # Enough pages are done -> break early
                break

            # Otherwise, wait poll_interval seconds, then re-check
            time.sleep(poll_interval)

        # Once we exit the loop (due to fraction reached or time up),
        # we retrieve *all* data for that bulk_search_id. This includes
        # both completed and possibly incomplete pages, but typically
        # you'll get mostly complete data at this point.
        full_data = self.pull_data(bulk_search_id=bulk_search_id)
        return full_data

    def simple_bulk_search(
        self,
        target_list: list,
        extract_html: bool = False,
        poll_interval: float = 2.0,
        wait_time: float = 30.0,
        completion_fraction: float = 1
    ) -> list:
        """
        Performs a bulk search on a list of URLs that may exceed 1000 elements.
        The list is first split into chunks (of at most 1000 URLs each). In one loop,
        a bulk search is started for each chunk (asynchronously) and the bulk search IDs
        are recorded. In a second loop, the function collects the results from each
        bulk search by polling until either the desired fraction of links have completed
        or the maximum wait time has elapsed.

        :param target_list: List of URLs to search.
        :param extract_html: If True, includes HTML content in the search results.
        :param poll_interval: How frequently (in seconds) to poll for bulk search results.
        :param wait_time: Maximum time (in seconds) to wait for each bulk search's results.
        :param completion_fraction: Fraction of completed results required to stop polling early.
        :return: List of PageData objects representing the search results.
        :raises ValueError: If target_list is not a non-empty list.
        """
        if not isinstance(target_list, list) or not target_list:
            raise ValueError("simple_bulk_search requires a non-empty list of URLs.")

        # Split the list into chunks of at most 1000 URLs each.
        sub_lists = _split_into_equal_sub_lists(target_list, max_size=1000)
        bulk_search_jobs = []

        # First loop: Initiate all bulk searches asynchronously.
        for sub_list in sub_lists:
            bulk_info = self.bulk_search(target_list=sub_list, extract_html=extract_html)
            bulk_search_id = bulk_info["bulk_search_id"]
            bulk_search_jobs.append((bulk_search_id, sub_list))

        # Second loop: Collect the results from each bulk search.
        all_results = []
        for bulk_search_id, sub_list in bulk_search_jobs:
            chunk_results = self.collect_results(
                bulk_search_id=bulk_search_id,
                target_links=sub_list,
                wait_time=wait_time,
                poll_interval=poll_interval,
                completion_fraction=completion_fraction
            )
            all_results.extend(chunk_results)

        return all_results



    def crawl(
        self,
        start_url: str,
        max_depth: int = 2,
        scrape_full_html: bool = False,
        remove_link_duplicates: bool = True,
        poll_interval: float = 2.0,
        wait_time_per_depth: float = 30.0,
        completion_fraction: float = 0.975
    ) -> list:
        """
        Recursively crawls the given start_url up to `max_depth` levels deep.
        - Depth 0: single stealth search on start_url.
        - Depth 1..N: gather unique same-domain links, do (possibly multiple) bulk_search(es) + collect_results.
        - Keep track of visited links to avoid duplicates.
        - Attach a `depth` attribute to each returned PageData.

        Returns a list of all PageData objects discovered (depth 0 through max_depth).
        """
        # Parse the domain from the start_url so we only crawl links on the same domain
        start_domain = urlparse(start_url).netloc.lower()
        visited_urls = set()
        all_results = []

        # ----- Depth 0: Single stealth search -----
        initial_page = self.search(
            url=start_url,
            search_type="stealth_search",
            scrape_full_html=scrape_full_html,
            remove_link_duplicates=remove_link_duplicates
        )
        # Dynamically store the depth
        initial_page.depth = 0
        all_results.append(initial_page)
        visited_urls.add(initial_page.url)

        # Helper to get same-domain links from a PageData object
        def same_domain_links(page_data):
            """
            Returns all same-domain links from a PageData (both internal & external).
            """
            combined = page_data.internal_links + page_data.external_links
            return [
                link for link in combined
                if urlparse(link).netloc.lower() == start_domain
            ]

        # Build the links for the next depth from the initial page
        current_depth_links = []
        for link in same_domain_links(initial_page):
            if link not in visited_urls:
                current_depth_links.append(link)
                visited_urls.add(link)

        # ----- Depth 1..max_depth -----
        depth = 1
        while depth <= max_depth and current_depth_links:
            # We may need multiple bulk searches if we have > 1000 links
            sub_lists = _split_into_equal_sub_lists(
                current_depth_links, 
                max_size=1000
            )

            # We will collect PageData objects from all sub-lists
            new_pages_this_depth = []
            for sub_list in sub_lists:
                # 1) Send bulk_search request for sub_list
                bulk_info = self.bulk_search(
                    target_list=sub_list,
                    extract_html=scrape_full_html
                )

                # 2) Wait/poll until enough are complete or time's up
                chunk_pages = self.collect_results(
                    bulk_search_id=bulk_info["bulk_search_id"],
                    target_links=sub_list,
                    wait_time=wait_time_per_depth,
                    poll_interval=poll_interval,
                    completion_fraction=completion_fraction
                )
                new_pages_this_depth.extend(chunk_pages)

            # Assign depth to each new PageData and store them
            for page_obj in new_pages_this_depth:
                page_obj.depth = depth
                all_results.append(page_obj)

            # 3) Gather the next set of same-domain links for the subsequent depth
            next_depth_links = []
            for page_obj in new_pages_this_depth:
                for link in same_domain_links(page_obj):
                    if link not in visited_urls:
                        next_depth_links.append(link)
                        visited_urls.add(link)

            # Prepare for the next loop
            current_depth_links = next_depth_links
            depth += 1

        # Return all discovered PageData objects at all depths
        return all_results

    def _post_and_parse(self, payload, *, timeout: float | None = None):
        """
        POST the payload, parse JSON, and raise if success=False.
        'timeout' overrides the default 20s for long-running ops like queue_scrape.
        """
        try:
            req_timeout = timeout if (timeout is not None and timeout > 0) else 20.0
            resp = requests.post(self.base_url, json=payload, timeout=req_timeout)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success", False):
                raise RuntimeError(
                    data.get("error", "Unknown error from API"),
                    data
                )
            return data
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP error: {e}")