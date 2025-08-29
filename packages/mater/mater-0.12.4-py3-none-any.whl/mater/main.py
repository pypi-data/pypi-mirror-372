"""
This module uses the MATER class to analyse scenarios.
"""

import os
import runpy
import sys

import click

import mater
from mater import Mater


@click.group()
def cli():
    """MATER application to run a model from an excel input file and visualize the outputs."""
    pass


@cli.command(
    context_settings={"show_default": True},
    no_args_is_help=True,
    help="Simulate the mater model from a specific excel template file.",
)
@click.option(
    "-i", "--input-file", type=str, help="Name of the excel input file. It must be in your working directory."
)
@click.option("-o", "--output-folder", type=str, default="run0", help="Name of the folder where the outpus are stored.")
@click.option("-s", "--start-time", type=int, default=1901, help="The initial time step.")
@click.option("-e", "--end-time", type=int, default=2100, help="The final time step.")
@click.option("-f", "--time-frequency", type=str, default="YS", help="The final time step.")
def run(input_file: str, output_folder: str, start_time: int, end_time: int, time_frequency: str):
    model = Mater()
    model.run_from_excel(
        output_folder,
        input_file,
        simulation_start_time=start_time,
        simulation_end_time=end_time,
        time_frequency=time_frequency,
    )


@cli.command(
    context_settings={"show_default": True},
    no_args_is_help=True,
    help="Plot the results of a mater simulation into a user interface.",
)
@click.option("-o", "--output-folder", type=str, help="Name of the folder where the outpus are stored.")
def plot(output_folder: str):
    # Find the path of the plot.py file inside the mater module
    streamlit_script_path = os.path.join(os.path.dirname(mater.__file__), "plot.py")
    sys.argv = ["streamlit", "run", streamlit_script_path, "--", f"--output-folder={output_folder}"]
    runpy.run_module("streamlit", run_name="__main__")
