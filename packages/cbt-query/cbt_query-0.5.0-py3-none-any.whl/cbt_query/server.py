import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import httpx
from mcp.server.fastmcp import FastMCP

# setup logging
logger = logging.getLogger(__name__)

# get base URL from environment variable
CBT_SERVER_URL = os.environ.get("CBT_SERVER_URL")
if not CBT_SERVER_URL:
    raise EnvironmentError("CBT_SERVER_URL environment variable not set")

DEFAULT_BASE_URL = CBT_SERVER_URL
DEFAULT_TIMEOUT = 30

# initialize FastMCP server
mcp = FastMCP("cbt_query")


async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    simple function to fetch JSON data from a URL.
    
    Args:
        url: the URL to fetch from
        params: optional request parameters
        
    Returns:
        parsed JSON data
    """
    logger.debug(f"fetching from {url} with params: {params}")
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            logger.debug(f"response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.debug(f"response data keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
            return data
    except Exception as e:
        logger.error(f"fetch failed for {url}: {e}")
        raise


def format_list_param(param: Union[str, List[str]]) -> str:
    """format parameter for API request - join list with semicolon"""
    if isinstance(param, list):
        return ";".join(param)
    return param


def extract_base_url(full_url: str, endpoint: str) -> str:
    """extract base URL by removing endpoint"""
    return full_url.replace(endpoint, "")


@mcp.tool()
async def query_all_cases(url: str = f"{DEFAULT_BASE_URL}/query_all_cases") -> List[Any]:
    """Get all cases from the query server."""
    data = await fetch_json(url)
    return data.get("result", data)


@mcp.tool()
async def query_all_files(url: str = f"{DEFAULT_BASE_URL}/query_all_files") -> List[Any]:
    """Get all files from the query server."""
    data = await fetch_json(url)
    return data.get("result", data)


@mcp.tool()
async def query_by_case(case_name: str, url: str = f"{DEFAULT_BASE_URL}/query_by_case") -> Dict[str, Any]:
    """Get coverage mapping result by case name."""
    if not case_name:
        raise ValueError("case_name cannot be empty")
    
    params = {"cases": case_name}
    return await fetch_json(url, params)


@mcp.tool()
async def query(
    file_name: Optional[Union[str, List[str]]] = None, 
    funcs: Optional[Union[str, List[str]]] = None, 
    url: str = f"{DEFAULT_BASE_URL}/query"
) -> Any:
    """Query cases by files and/or functions.
    
    Usage examples:
    - query(file_name="file1.cpp")
    - query(funcs="function1")
    - query(file_name=["file1.cpp", "file2.cpp"], funcs=["func1", "func2"])
    """
    if not file_name and not funcs:
        raise ValueError("At least one of file_name or funcs must be provided")
    
    params = {}
    if file_name:
        params["files"] = format_list_param(file_name)
    if funcs:
        params["funcs"] = format_list_param(funcs)
    
    data = await fetch_json(url, params)
    return data.get("result", data)


@mcp.tool()
async def query_test_similarity(
    test_cases1: Union[str, List[str]],
    test_cases2: Union[str, List[str]],
    use_turtle_names: bool = False,
    filter_test_list: bool = False,
    url: str = f"{DEFAULT_BASE_URL}/query_test_similarity"
) -> Dict[str, Any]:
    """Compare test coverage similarity between two test lists.
    
    Args:
        test_cases1: First test list (test names or aliases, can be string or list)
        test_cases2: Second test list (test names or aliases, can be string or list)
        use_turtle_names: Whether to convert TURTLE test names (default: False)
        filter_test_list: Whether to enable filtered test list analysis (default: False)
        url: API endpoint URL (default: uses CBT_SERVER_URL)
    
    Returns:
        Test similarity comparison results including similarity scores, coverage data, and filtered lists
    
    Usage examples:
    - query_test_similarity("L0", "L1")
    - query_test_similarity(["test1", "test2"], ["test3", "test4"])
    - query_test_similarity("trt_mod_test", "infer_test", filter_test_list=True)
    - query_test_similarity(test_cases1="L0", test_cases2="L1", use_turtle_names=True)
    """
    # Clean and validate input parameters
    def clean_test_cases(test_cases):
        """Clean test cases by stripping whitespace and filtering empty strings"""
        if isinstance(test_cases, str):
            # For string input, split by semicolon and clean each item
            cleaned = [item.strip() for item in test_cases.split(';') if item.strip()]
            return cleaned
        elif isinstance(test_cases, list):
            # For list input, strip each item and filter empty strings
            cleaned = [item.strip() for item in test_cases if item and item.strip()]
            return cleaned
        else:
            raise ValueError(f"test_cases must be string or list, got {type(test_cases)}")
    
    # Clean both test case inputs
    cleaned_test_cases1 = clean_test_cases(test_cases1)
    cleaned_test_cases2 = clean_test_cases(test_cases2)
    
    # Validate that we have non-empty lists after cleaning
    if not cleaned_test_cases1:
        raise ValueError("test_cases1 is empty or contains only whitespace/empty strings after cleaning")
    if not cleaned_test_cases2:
        raise ValueError("test_cases2 is empty or contains only whitespace/empty strings after cleaning")
    
    params = {
        "test_list1": format_list_param(cleaned_test_cases1),
        "test_list2": format_list_param(cleaned_test_cases2)
    }
    
    # Add optional boolean parameters
    if use_turtle_names:
        params["use_turtle_names"] = "true"
    if filter_test_list:
        params["filter_test_list"] = "true"
    
    return await fetch_json(url, params)
