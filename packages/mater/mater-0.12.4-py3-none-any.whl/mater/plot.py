"""Create a UI to plot and filter the outputs"""

import argparse
import os
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # headless—no GUI

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from mater import Mater

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--output-folder",
    type=str,
    required=True,
    help="Name of the folder where the outputs are stored.",
)
args = parser.parse_args()


# Define a callback to update session state
def update_time():
    st.session_state.time_value = st.session_state.time


def update_times():
    st.session_state.times_value = st.session_state.times


@st.cache_data
def get_data_list(run_name: str):
    run_folder_path = os.path.join(os.getcwd(), run_name)
    data_list = os.listdir(run_folder_path)
    return data_list


@st.cache_data
def get_data(data_name: str, run_name: str):
    model = Mater()
    model.run_name = run_name
    df = model.get(data_name)
    # Groupby to get rid off age_cohort
    level_list = list(df.index.names)
    if "age_cohort" in level_list:
        level_list.remove("age_cohort")
        df = df.groupby(level=level_list).sum()
    return df


@st.cache_data
def df_filtering(df: pd.DataFrame, level_values: Dict[str, List[str]]):
    # Filter the dataframe to plot : create a mask
    index = pd.MultiIndex.from_product(
        [level_values[level] for level in level_values.keys()],
        names=level_values.keys(),
    )
    mask = pd.DataFrame(data=1, index=index, columns=df.columns)

    # Filter the dataframe to plot with the element selection
    filtered_df = df.mul(mask).dropna(how="all")
    return filtered_df


def get_closest_date(target_date: pd.Timestamp, date_index: pd.DataFrame.columns):
    """
    Finds the closest available date in `date_index` to `target_date`.
    """
    target_date = pd.to_datetime(target_date, utc=True)
    closest_index = date_index.get_indexer([target_date], method="nearest")[0]
    return date_index[closest_index]


def plot_df(df: pd.DataFrame, data_name: str, plot: bool, all_data: bool, plot_type: str):
    if plot & all_data:
        # Select time
        # Does not handle h, min or s or lower frequencies
        min_time = df.columns.min().date()
        max_time = df.columns.max().date()

        if plot_type == "pie":
            # Initialize session state for the slider
            if "time_value" not in st.session_state:
                st.session_state.time_value = max_time  # Default value
            time = st.sidebar.slider(
                "time",
                min_time,
                max_time,
                value=st.session_state.time_value,  # Use session state as initial value
                key="time",
                on_change=update_time,
            )
            # Transform back to date
            date_time = get_closest_date(pd.to_datetime(time, utc=True), df.columns)
            # plot
            fig, ax = plt.subplots()
            # Filter
            df[date_time].T.plot(ax=ax, kind=plot_type, autopct="%1.1f%%")
            ax.set_title(data_name)
            st.pyplot(fig)
        else:
            # Initialize session state for the slider
            if "times_value" not in st.session_state:
                st.session_state.times_value = (min_time, max_time)  # Default value
            time_steps = st.sidebar.slider(
                "time",
                min_time,
                max_time,
                (st.session_state.times_value[0], st.session_state.times_value[1]),
                key="times",
                on_change=update_times,
            )
            # Transform back to date
            date_time_steps = [
                get_closest_date(pd.to_datetime(time_steps[0], utc=True), df.columns),
                get_closest_date(pd.to_datetime(time_steps[1], utc=True), df.columns),
            ]
            # Filter
            df_time_filtered = df.loc[:, date_time_steps[0] : date_time_steps[1]]
            if plot_type == "table":
                st.dataframe(df_time_filtered, use_container_width=True)
            else:
                # plot
                fig, ax = plt.subplots()
                df_time_filtered.T.plot(ax=ax, kind=plot_type)
                ax.set_title(data_name)
                st.pyplot(fig)


# Main app

# Detect the system theme
plt.style.use("default")  # Use the default (light) theme

st.sidebar.title("MATER visualization")

# Get the list of the data available for plotting
data_list = get_data_list(args.output_folder)

# Create the data selector
data_name = st.sidebar.selectbox("data", data_list)

# Retrieve the dataframe (cached data)
df = get_data(data_name, args.output_folder)

# visualization type
plot_types = ["line", "area", "pie", "table"]
plot_type = st.sidebar.radio("visualization type", plot_types, horizontal=True)

# plot ?
plot = True
# all data ?
all_data = True

# Select item
level_values = {}
st.sidebar.header("Element selection")
for level in df.index.levels:
    item_list = list(level.unique())
    data = st.sidebar.multiselect(level.name, item_list, item_list[0])
    if not data:
        st.error(f"Please select at least one {level.name}.")
        all_data = False
    level_values[level.name] = data

filtered_df = df_filtering(df, level_values)
if filtered_df.empty & all_data:
    st.error("Please select another element combination.")
    plot = False

# Plot the dataframe with matplotlib
plot_df(filtered_df, data_name, plot, all_data, plot_type)
