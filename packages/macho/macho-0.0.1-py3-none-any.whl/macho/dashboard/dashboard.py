# --------------- Imports ---------------

from macho.logging import get_logger

import streamlit as st

import os
import tempfile

# --------------- Logging setup ---------------

logger = get_logger(__name__)

# --------------- JSON Data Path ---------------

JSON_DATA_PATH = os.environ.get(
    "MACHO_CACHE_JSON_PATH",
    os.path.join(tempfile.gettempdir(), "macho_cache.json")
)

# --------------- Main Page ---------------

st.set_page_config(
    page_title="Macho Caching Metrics",
    page_icon="👋",
    layout="wide"
)

st.title("Welcome to Macho Metrics Dashboard! 👋")
st.divider()
st.markdown(
    """
    Macho's extensive metrics dashboard provides you with concrete data for optimizing, analyzing,
    and streamlining caching opreations.

    **👈 Select options from the navigation bar** to views metrics.

    ### For further information regarding Macho:
    - [Github](https://github.com/MassivelyOverthinking/Macho)
    """
)
    