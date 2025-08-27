# --------------- Imports ---------------

from macho.dashboard import load_from_json

from macho.errors import MetricsLifespanException

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------- Lifespan Metrics ---------------

st.title("Entry Lifespan Data ⌛")
st.divider()
st.subheader("Metrics & Data visualisation regarding individual and overall lifespan of caching entries.")

# Access stored cache in Session State
try:
    if "macho_metrics" not in st.session_state:
        st.session_state["macho_metrics"] = load_from_json()

    macho_cache_metrics = st.session_state["macho_metrics"]
except Exception as e:
    st.error(f"Failed ot load cache {e}")
    st.stop()

# Manage Streamlit tabs
tabs = st.tabs(["📊 Summary", "📉 Histogram", "📦 Box Plot"])

if macho_cache_metrics is None:
    st.error("No metrics found in current session state")
elif not isinstance(macho_cache_metrics, (dict, list)):
    st.error("The object currently in Session State is not a valid Cache-object")
else:
    if isinstance(macho_cache_metrics, list): # Shared Cache

        try:
            lifespan_data = [shard["lifespan_metrics"] for shard in macho_cache_metrics]
            all_lifespans = [
                {"Shard": i, "Lifespan": val}
                for i, shard in enumerate(lifespan_data)
                for val in shard["all_lifespans"]
            ]
        except MetricsLifespanException as e:
            st.error(f"No lifespan data currently available {e}")
        else:
            shard_df = pd.DataFrame([
                {
                    "Shard": index,
                    "Max": data["max"],
                    "Min": data["min"],
                    "Count": data["count"],
                    "Total": data["total"],
                    "Average": data["average"],
                    "Median": data["median"]
                }
                for index, data in enumerate(lifespan_data)
            ])

            with tabs[0]:
                st.subheader("Summary of Lifespan Metrics")
                st.dataframe(shard_df)
                st.plotly_chart(px.bar(
                    shard_df.melt(id_vars="Shard", var_name="Metric", value_name="Value"),
                    x="Shard",
                    y="Value",
                    color="Metric",
                    barmode="group",
                    title="Lifespan Metrics pr. Shard"
                ))

                with st.expander("View Raw Summary Table"):
                    st.dataframe(shard_df)

            with tabs[1]:
                st.subheader("Distribution of Lifespan Metrics")
                lfsp_data = pd.DataFrame(all_lifespans)
                st.dataframe(lfsp_data)
                bins = st.slider("Number of bins", min_value=10, max_value=100, value=30)
                st.plotly_chart(px.histogram(
                    lfsp_data,
                    x="Lifespan",
                    color="Shard",
                    nbins=bins,
                    barmode="overlay",
                    opacity=0.6,
                    title="Entry Lifespan Distribution pr. shard"
                ))

                if st.checkbox("Show Raw Lifespan Data"):
                    st.dataframe(lfsp_data)

            with tabs[2]:
                st.subheader("Box Plot pr. Shard")
                st.plotly_chart(px.box(
                    lfsp_data,
                    x="Shard",
                    y="Lifespan",
                    points="outliers",
                    title="Lifespan Spread pr. Shard"
                ))
    
    else: # Individual Cache
        st.subheader("Single Cache Lifespan Metrics")

        try:
            lifespan_data = macho_cache_metrics["lifespan_metrics"]
            entry_lifespans = lifespan_data["all_lifespans"]
        except MetricsLifespanException as e:
            st.error(f"No lifespan data currently available {e}")
        else:
            lifespan_df = pd.DataFrame([
                {"Metric": k.capitalize(), "Value": v}
                for k, v in lifespan_data.items()
            ])

            with tabs[0]:
                st.subheader("Summary of Lifespan Metrics")
                st.dataframe(lifespan_df)
                st.plotly_chart(px.bar(
                    lifespan_df,
                    x="Metric",
                    y="Value",
                    title="Lifespan Metrics"
                ))

                with st.expander("View Raw Summary Data"):
                    st.dataframe(lifespan_df)

            with tabs[1]:
                st.subheader("Distribution of Entry Lifespans")
                new_df = pd.DataFrame(entry_lifespans, columns=["Lifespan"])
                bins = st.slider("Number of bins", min_value=10, max_value=100, value=30)
                if entry_lifespans:
                    st.plotly_chart(px.histogram(
                        new_df,
                        x="Lifespan",
                        nbins=bins,
                        title="Entry Lifespan Distribution",
                        labels={"Value": "Lifespan(s)"},
                        opacity=0.7
                    ))

                    if st.checkbox("Show Raw Lifespan Data"):
                        st.dataframe(new_df)

            with tabs[2]:
                st.subheader("Box Plot of Lifespans")
                if entry_lifespans:
                    df = pd.DataFrame({"Lifespan": entry_lifespans})
                    st.plotly_chart(px.box(
                        df, 
                        y="Lifespan",
                        points="outliers",
                        title="Lifespan Spread"
                    ))
