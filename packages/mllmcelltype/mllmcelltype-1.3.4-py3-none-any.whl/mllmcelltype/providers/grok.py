"""Grok provider module for LLMCellType."""

import json
import time
from typing import Optional

import requests

from ..logger import write_log


def process_grok(
    prompt: str, model: str, api_key: str, base_url: Optional[str] = None
) -> list[str]:
    """Process request using Grok models from xAI.

    Args:
        prompt: The prompt to send to the API
        model: The model name (e.g., 'grok-3-latest')
        api_key: xAI API key
        base_url: Optional custom base URL

    Returns:
        List[str]: Processed responses, one per cluster

    """
    write_log(f"Starting Grok API request with model: {model}")

    # Check if API key is provided and not empty
    if not api_key:
        error_msg = "Grok API key is missing or empty"
        write_log(f"ERROR: {error_msg}")
        raise ValueError(error_msg)

    # 使用自定义URL或默认URL
    if base_url:
        from ..url_utils import validate_base_url

        if not validate_base_url(base_url):
            raise ValueError(f"Invalid base URL: {base_url}")
        url = base_url
        write_log(f"Using custom base URL: {url}")
    else:
        from ..url_utils import get_default_api_url

        url = get_default_api_url("grok")
        write_log(f"Using default URL: {url}")

    write_log(f"Using model: {model}")

    # Process all input at once
    write_log("Processing input in 1 chunk")

    # Prepare the request body
    body = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    write_log("Sending API request...")
    # Make the API request
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(url=url, headers=headers, data=json.dumps(body), timeout=30)

            # Check for errors
            if response.status_code != 200:
                error_message = response.json()
                write_log(
                    f"ERROR: Grok API request failed: {error_message.get('error', {}).get('message', 'Unknown error')}"
                )

                # If rate limited, wait and retry
                if response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = retry_delay * (2**attempt)
                    write_log(f"Rate limited. Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()

            # Parse the response
            content = response.json()
            res = content["choices"][0]["message"]["content"].strip().split("\n")
            write_log(f"Got response with {len(res)} lines")
            write_log(f"Raw response from Grok:\n{res}")

            # Success, exit retry loop
            write_log("All chunks processed successfully")
            # Clean up results (remove commas at the end of lines)
            return [line.rstrip(",") for line in res]

        except Exception as e:
            write_log(f"Error during API call (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2**attempt)
                write_log(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                raise

    # This should not be reached if all retries fail (an exception would be raised)
    return []
