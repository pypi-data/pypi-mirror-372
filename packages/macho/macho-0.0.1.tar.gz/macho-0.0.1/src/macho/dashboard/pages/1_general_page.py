# --------------- Imports ---------------

from macho.dashboard import load_from_json
from macho.utility import extract_general_info

import streamlit as st

# --------------- General Information ---------------

st.title("General Cache Information ℹ️")
st.divider()

# Access stored cache data in Session State
try:
    if "macho_metrics" not in st.session_state:
        st.session_state["macho_metrics"] = load_from_json()    # Loads data from persistent storage.

    macho_cache_metrics = st.session_state["macho_metrics"]
except Exception as e:
    st.error(f"Failed to load cache data {e}")
    st.stop()


if macho_cache_metrics is None:
    st.error("No caching metrics found in session state")
elif not isinstance(macho_cache_metrics, (dict, list)):
    st.error("The object currently in Session State is not a valid Cache-class object")
else:
    if isinstance(macho_cache_metrics, list):
        st.subheader("Shared Cache Information")
        for index, shard in enumerate(macho_cache_metrics):
            st.markdown(f"## Shard {index}")
            st.json(extract_general_info(shard))
    else:
        st.subheader("Single Cache Information")
        st.json(extract_general_info(macho_cache_metrics))
