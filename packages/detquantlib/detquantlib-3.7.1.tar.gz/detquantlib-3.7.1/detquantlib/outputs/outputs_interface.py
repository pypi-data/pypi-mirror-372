# Python built-in packages
import json
from pathlib import Path

# Third-party packages
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class OutputItem:
    """A class to easily manage, store and export a model output."""

    def __init__(
        self,
        data=None,
        filename: str = None,
        extension: str = None,
        sub_path: str = None,
        export_options: dict = None,
    ):
        """
        Constructor method.

        Args:
            data: Output data
            filename: Filename to be used when exporting the output data
            extension: File extension to be used when exporting the output data
            sub_path: Within the output base directory, indicates the sub-path (if any) of the
                folder where the output data should be exported
            export_options: Additional options for the function exporting the output data to a file
        """
        self.data = data
        self.filename = filename
        self.extension = extension
        self.sub_path = sub_path
        self.export_options = dict() if export_options is None else export_options

    def export_to_file(self, folder_dir: Path = None):
        """
        Exports the model output to a file.

        Args:
            folder_dir: Base directory of the folder containing all model outputs

        Raises:
            ValueError: Raises an error if the output file extension is not supported
        """
        # Define output folder directory, and create it if it doesn't exist yet
        if folder_dir is None:
            folder_dir = PathDefinitions.get_outputs_folder_dir()
        if self.sub_path is not None:
            folder_dir = folder_dir.joinpath(self.sub_path)
        folder_dir.mkdir(parents=True, exist_ok=True)

        # Define output file directory
        filename = f"{self.filename}.{self.extension}"
        file_dir = folder_dir.joinpath(filename)

        # Create output file
        if self.extension == "csv":
            self.export_to_csv(file_dir)
        elif self.extension == "json":
            self.export_to_json(file_dir)
        elif self.extension == "html":
            self.export_to_html(file_dir)
        elif self.extension == "npz":
            self.export_to_npz(file_dir)
        else:
            raise ValueError("Invalid output file extension.")

    def export_to_csv(self, file_dir: Path):
        """
        Exports the model output to a csv file.

        Args:
            file_dir: Directory of the output file

        Raises:
            TypeError: Raises an error if the data type is not supported
        """
        data_type = type(self.data)
        if data_type is pd.DataFrame:
            self.data.to_csv(file_dir, **self.export_options)
        else:
            raise TypeError(f"Exporting data type {data_type} to csv file is not supported.")

    def export_to_json(self, file_dir: Path):
        """
        Exports the model output to a json file.

        Args:
            file_dir: Directory of the output file

        Raises:
            TypeError: Raises an error if the data type is not supported
        """
        data_type = type(self.data)
        if data_type is dict:
            with open(file_dir, "w") as f:
                json.dump(self.data, f, indent=4, **self.export_options)
        else:
            raise TypeError(f"Exporting data type {data_type} to json file is not supported.")

    def export_to_html(self, file_dir: Path):
        """
        Exports the model output to a html file.

        Args:
            file_dir: Directory of the output file

        Raises:
            TypeError: Raises an error if the data type is not supported
        """
        data_type = type(self.data)
        if data_type is go.Figure:
            self.data.write_html(file_dir, **self.export_options)
        else:
            raise TypeError(f"Exporting data type {data_type} to html file is not supported.")

    def export_to_npz(self, file_dir: Path):
        """
        Exports the model output to a npz file.

        Args:
            file_dir: Directory of the output file

        Raises:
            TypeError: Raises an error if the data type is not supported
        """
        data_type = type(self.data)
        if data_type is np.ndarray:
            np.savez_compressed(file_dir, data=self.data, **self.export_options)
        else:
            raise TypeError(f"Exporting data type {data_type} to npz file is not supported.")


class OutputSet:
    """A short class to store all OutputItem objects into a single object."""

    def __init__(self, output_items: list[OutputItem] = None):
        """
        Constructor method.

        Args:
            output_items: List of OutputItem objects
        """
        if output_items is None:
            output_items = list()
        self.output_items = output_items

    def add_item(self, data, filename: str, extension: str, sub_path: str = None):
        """
        Creates an OutputItem object and adds it to the OutputSet list.

        Args:
            data: Output data
            filename: Filename to be used when exporting the output data
            extension: File extension to be used when exporting the output data
            sub_path: Within the output base directory, indicates the sub-path (if any) of the
                folder where the output data should be exported
        """
        # Create OutputItem object
        item = OutputItem(data=data, filename=filename, extension=extension, sub_path=sub_path)
        # Append to OutputSet list
        self.output_items.append(item)


class PathDefinitions:
    """A class containing hard-coded path definitions."""

    @staticmethod
    def outputs_folder():
        return "Outputs"

    @staticmethod
    def outputs_plotly_folder():
        return "PlotlyFigures"

    @staticmethod
    def get_outputs_folder_dir():
        # Base directory of the folder containing all model outputs
        return Path.cwd().joinpath(PathDefinitions.outputs_folder())

    @staticmethod
    def get_outputs_plotly_folder_dir():
        # Directory of the output folder containing all plotly figures
        base_dir = PathDefinitions.get_outputs_folder_dir()
        return base_dir.joinpath(PathDefinitions.outputs_plotly_folder())
