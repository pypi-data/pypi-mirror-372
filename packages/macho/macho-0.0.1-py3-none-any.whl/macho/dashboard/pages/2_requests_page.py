# --------------- Imports ---------------

from macho.dashboard import load_from_json

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------- Requests Metrics ---------------

st.title("Cache Requests Data 📚")
st.divider()
st.subheader("Metrics & Data visualisation regarding total requests made towards the Cache.")

# Access stored cache in Session State
try:
    if "macho_metrics" not in st.session_state:
        st.session_state["macho_metrics"] = load_from_json()

    macho_cache_metrics = st.session_state["macho_metrics"]
except Exception as e:
    st.error(f"Failed ot load cache {e}")
    st.stop()

if macho_cache_metrics is None:
    st.error("No metrics found in current session state")
elif not isinstance(macho_cache_metrics, (dict, list)):
    st.error("The obejct currently in Session State is not a valid Cache-object")
else:
    if isinstance(macho_cache_metrics, list):
        st.subheader("Shared Cache Metrics")

        shard_df = pd.DataFrame([
            {
                "Shard": index,
                "Hit Ratio": shard["hit_ratio"],
                "Hits": shard["hits"],
                "Misses": shard["misses"],
                "Evictions": shard["evictions"]
            }
            for index, shard in enumerate(macho_cache_metrics)
        ])

        st.plotly_chart(px.bar(
            shard_df,
            x="Shard",
            y=["Hits", "Misses", "Evictions"],
            barmode="group",
            title="Cache activity pr. Caching System"
        ))

        st.plotly_chart(px.line(
            shard_df,
            x="Shard",
            y="Hit Ratio",
            title="Hit ratio pr. second"
        ))

    else:
        st.subheader("Single Cache Metrics")

        single_df = pd.DataFrame([{
            "Hits": macho_cache_metrics["hits"],
            "Misses": macho_cache_metrics["misses"],
            "Evictions": macho_cache_metrics["evictions"],
            "Hit Ratio": macho_cache_metrics["hit_ratio"]
        }])

        st.plotly_chart(px.bar(
            single_df.melt(var_name="Metric", value_name="Value"),
            x="Metric",
            y="Value",
            title="Single Cachen Operations"
        ))








