# Python built-in packages
from pathlib import Path

# Third-party packages
import plotly.graph_objects as go
import plotly.io as pio


def get_default_plotly_folder_dir():
    # Default path to output folder containing plotly figures.
    return Path.cwd().joinpath("Outputs", "PlotlyFigures")


def set_standard_layout(fig: go.Figure) -> go.Figure:
    """
    Short helper function to improve and standardize the layout of plotly figures.

    Args:
        fig: Plotly figure

    Returns:
        Plotly figure with updated layout options
    """
    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis=dict(showline=True, linecolor="black", showgrid=False, ticks="outside"),
        yaxis=dict(showline=True, linecolor="black", showgrid=True, ticks="outside"),
        hovermode="x",
    )
    return fig


def save_plotly_fig_to_json(
    fig: go.Figure,
    filename: str,
    folder_dir: Path = get_default_plotly_folder_dir(),
    standard_layout: bool = True,
):
    """
    Saves a plotly figure object to a json file.

    Args:
        fig: Plotly figure
        filename: Name of json file in which plotly figure will be saved
        folder_dir: Folder directory where the json file will be saved
        standard_layout: If true, enforces a standard plotly layout
    """
    # Create plotly folder if it doesn't exist yet
    folder_dir.mkdir(parents=True, exist_ok=True)

    # Define json file directory
    file_dir = folder_dir.joinpath(f"{filename}.json")

    # Adjust figure layout
    if standard_layout:
        fig = set_standard_layout(fig)

    # Save figure to json
    fig_json = fig.to_json()
    with open(file_dir, "w") as f:
        f.write(fig_json)


def save_plotly_fig_to_html(
    fig: go.Figure,
    filename: str,
    folder_dir: Path = get_default_plotly_folder_dir(),
    standard_layout: bool = True,
):
    """
    Saves a plotly figure object to an html file.

    Args:
        fig: Plotly figure
        filename: Name of html file in which plotly figure will be saved
        folder_dir: Folder directory where the html file will be saved
        standard_layout: If true, enforces a standard plotly layout
    """
    # Create plotly folder if it doesn't exist yet
    folder_dir.mkdir(parents=True, exist_ok=True)

    # Define html file directory
    file_dir = folder_dir.joinpath(f"{filename}.html")

    # Adjust figure layout
    if standard_layout:
        fig = set_standard_layout(fig)

    # Save figure to html
    fig.write_html(file_dir)


def show_plotly_fig_json(filename: str, folder_dir: Path = get_default_plotly_folder_dir()):
    """
    Short helper function to display a plotly figure stored in a json file.

    Args:
        filename: Name of json file containing the plotly figure
        folder_dir: Folder directory containing the json file
    """
    # Get json file directory
    file_dir = folder_dir.joinpath(f"{filename}.json")

    # Load figure from json
    with open(file_dir, "r") as f:
        fig_json = f.read()
    fig = pio.from_json(fig_json)

    # Display figure
    fig.show()
