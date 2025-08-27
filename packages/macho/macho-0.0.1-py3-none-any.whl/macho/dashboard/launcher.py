# --------------- Imports ---------------

from macho.logging import get_logger
from macho.main import Cache

from typing import Dict, Any, Union, List

import streamlit.web.cli as stcli

import json
import os
import tempfile
import sys


# --------------- Logging setup ---------------

logger = get_logger(__name__)       # Get logger equipped with Rotating File Handler.

# --------------- JSON Data Path ---------------

JSON_DATA_PATH = os.environ.get(
    "MACHO_CACHE_JSON_PATH",
    os.path.join(tempfile.gettempdir(), "macho_cache.json")
)

# --------------- Streamlit Dashboard Launcher ---------------

def load_from_json() -> Union[Dict[str, Any], List[Dict[str, Any]]]:       # Loads data for Streamlit dashboard from persistent storage
    if not os.path.exists(JSON_DATA_PATH):
        raise FileNotFoundError(f"No data found in persistent storage")
    
    with open(JSON_DATA_PATH, "r", encoding='utf-8') as tmp: 
        metrics_data = json.load(tmp)   # Retreives data

    return metrics_data     # Returns data in a dictionary/list formats

def save_to_memory(data: Union[Dict, List[Dict]]) -> None:
    if not isinstance(data, (dict, list)):
        raise TypeError(f"Could not save to memory, as 'data' must be of Type: dict or list")
    
    with open(JSON_DATA_PATH, "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def launch_dashboard(cache: Cache) -> None:
    if not isinstance(cache, Cache):
        raise TypeError(f"Paramter 'cache' must be of Type: Cache, not {type(cache)}")
    
    macho_cache_metrics = cache.metrics
    
    save_to_memory(macho_cache_metrics)

    # Runs the Streamlit server from a subprocess
    script_path = os.path.abspath(__file__)
    dsh_dir = os.path.dirname(script_path)
    final_path = os.path.join(dsh_dir, "dashboard.py")

    logger.debug(f"Launching Streamlit dashboard from path {final_path}")

    sys.argv = ["streamlit", "run", final_path]
    sys.exit(stcli.main())