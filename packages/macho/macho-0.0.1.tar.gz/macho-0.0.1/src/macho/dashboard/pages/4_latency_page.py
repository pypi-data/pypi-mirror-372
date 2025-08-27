# --------------- Imports ---------------

from macho.dashboard import load_from_json

from macho.errors import MetricsLatencyException

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------- Latency Metrics ---------------

st.title("Function Latency Data ⏱️")
st.divider()
st.subheader("Metrics & Data visualisation of the time it takes to perform individual function calls.")

# Access stored cache in Session State
try:
    if "macho_metrics" not in st.session_state:
        st.session_state["macho_metrics"] = load_from_json()

    macho_cache_metrics = st.session_state["macho_metrics"]
except Exception as e:
    st.error(f"Failed ot load cache {e}")
    st.stop()

# Manage Streamlit Tabs
tabs = st.tabs(["📉 Line Charts", "📊 Histograms", "📦 Box Plots"])

if macho_cache_metrics is None:
    st.error("No metrics found in current session state")
elif not isinstance(macho_cache_metrics, (dict, list)):
    st.error("The object currently in Session State is not a valid Cache-object")
else:
    if isinstance(macho_cache_metrics, list): # shared cache

        try:
            shared_latency_data = [shard["latencies"] for shard in macho_cache_metrics]
            all_shared_latencies = [
                {"Shard": index, "Type": "Get", "Latency": get_l}
                for index, shard in enumerate(shared_latency_data)
                for get_l in shard["get_latency"]
            ] + [
                {"Shard": index, "Type": "Add", "Latency": add_l}
                for index, shard in enumerate(shared_latency_data)
                for add_l in shard["add_latency"]
            ]
        except MetricsLatencyException as e:
            st.error("No Latency Data currently available")
        else:
            shard_latency_df = pd.DataFrame([
                {
                    "Shard": index,
                    "Avg. Add Latency": data["add_latency_seconds"],
                    "Max Add Latency": data["max_add_latency"],
                    "Min Add Latency": data["min_add_latency"],
                    "Avg. Get Latency": data["get_latency_seconds"],
                    "Max Get Latency": data["max_get_latency"],
                    "Min Get Latency": data["min_get_latency"]
                }
                for index, data in enumerate(shared_latency_data)
            ])

            with tabs[0]:
                st.subheader("Line Charts for Cache Latency")
                st.dataframe(shard_latency_df)
                st.plotly_chart(px.line(
                    shard_latency_df.melt(id_vars="Shard", var_name="Metric", value_name="Latency(s)"),
                    x="Metric",
                    y="Latency(s)",
                    color="Metric",
                    markers=True,
                    title="Latency Metrics per Shard",
                    template="plotly"
                ))

                with st.expander("View Raw Summary Data"):
                    st.dataframe(shard_latency_df)

            with tabs[1]:
                st.subheader("Histograms for Cache Latencies")
                hist_latency_data = pd.DataFrame(all_shared_latencies)
                st.dataframe(hist_latency_data)

                shared_bins = st.slider(label="Number of bins", min_value=10, max_value=100, value=30)

                st.plotly_chart(px.histogram(
                    hist_latency_data,
                    x="Latency",
                    color="Type",
                    nbins=shared_bins,
                    barmode="overlay",
                    opacity=0.6,
                    title="Method Latency Distribution per Shard"
                ))

                if st.checkbox("Show Raw Latency Data"):
                    st.dataframe(all_shared_latencies)

            with tabs[2]:
                st.subheader("Box Plot per shard")
                st.plotly_chart(px.box(
                    all_shared_latencies,
                    x="Shard",
                    y="Latency",
                    points="outliers",
                    title="Latency Spread per Shard"
                ))
    else: # Single Cache
        st.subheader("Single Cache Latency Metrics")

        try:
            single_latency_data = macho_cache_metrics["latencies"]
            all_single_latencies = macho_cache_metrics["get_latency"] + macho_cache_metrics["add_latency"]
        except MetricsLatencyException as e:
            st.error(f"No latency data currently available {e}")
        else:
            latency_df = pd.DataFrame([
                {"Metric": key.capitalize(), "Value": value}
                for key, value in single_latency_data.items() 
            ])

            with tabs[0]:
                st.subheader("Line Charts for Cache Latency")
                st.dataframe(latency_df)
                st.plotly_chart(px.line(
                    latency_df,
                    x="Metric",
                    y="Value",
                    title="Latency Metrics"
                ))

                with st.expander("View Raw Latency Data"):
                    st.dataframe(latency_df)

            with tabs[1]:
                st.subheader("Histograms for Cache Latencies")
                all_entry_latency_data = pd.DataFrame(all_single_latencies, columns=["Latency"])

                single_bins = st.slider(label="Number of bins", min_value=10, max_value=100, value=30)

                if all_single_latencies:
                    st.plotly_chart(px.histogram(
                        all_entry_latency_data,
                        x="Latency",
                        nbins=single_bins,
                        title="Entry Latency Distribution",
                        labels={"Value": "Latency(s)"},
                        opacity=0.7
                    ))

                    if st.checkbox("Show Raw Latency Data"):
                        st.dataframe(all_entry_latency_data)

            with tabs[2]:
                st.subheader("Box Plot for Single Cache")
                if all_single_latencies:
                    df = pd.DataFrame({"Latency": all_single_latencies})
                    st.plotly_chart(px.box(
                        df,
                        y="Latency",
                        points="outliers",
                        title="Latency Spread"
                    ))