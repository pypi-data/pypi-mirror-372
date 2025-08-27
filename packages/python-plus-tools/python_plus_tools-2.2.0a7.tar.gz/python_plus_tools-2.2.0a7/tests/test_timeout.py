import requests
from requests.exceptions import Timeout
from typing import List


def fetch_url(
    main_url: str, backup_urls: List[str] = [], retries: int = 3, timeout: int = 5
):
    all_urls = [main_url] + backup_urls

    for idx, url in enumerate(all_urls):
        for attempt in range(retries + 1):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except Timeout as e:
                if attempt == retries:
                    if url != all_urls[-1]:
                        pass
                    break
    raise TimeoutError
