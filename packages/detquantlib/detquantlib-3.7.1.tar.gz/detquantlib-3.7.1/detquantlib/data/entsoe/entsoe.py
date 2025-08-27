# Python built-in packages
import shutil
from pathlib import Path

# Third-party packages
import pandas as pd

# Internal modules
from detquantlib.data.sftp.sftp import Sftp


class Entsoe:
    """
    A class that handles ENTSOE data, including importing and processing data from their SFTP
    server.
    """

    def __init__(self, sftp: Sftp = None):
        self.sftp = sftp

    @staticmethod
    def get_sftp_folder_dir_day_ahead_spot_prices():
        # Directory of SFTP folder containing day-ahead spot prices.
        return "/TP_export/EnergyPrices_12.1.D_r3/"

    @staticmethod
    def get_sftp_filename_day_ahead_spot_prices(year: int, month: int) -> str:
        """
        Name of SFTP files containing day-ahead spot prices.

        Args:
            year: Delivery year
            month: Delivery month

        Returns:
            Filename of day-ahead spot prices
        """
        year_str = str(year)
        month_str = str(month) if month >= 10 else f"0{month}"
        return f"{year_str}_{month_str}_EnergyPrices_12.1.D_r3.csv"

    def import_day_ahead_spot_prices_file_from_sftp(
        self, year: int, month: int, local_folder_dir: str
    ):
        """
        Downloads the file containing the day-ahead spot prices of a given delivery month from
        the ENTSOE SFTP server to a local directory.

        Args:
            year: Delivery year
            month: Delivery month
            local_folder_dir: Local directory where file will be copied
        """
        filename = Entsoe.get_sftp_filename_day_ahead_spot_prices(year=year, month=month)
        remote_folder_dir = Entsoe.get_sftp_folder_dir_day_ahead_spot_prices()
        remote_dir = f"/{remote_folder_dir}/{filename}"
        local_dir = f"{local_folder_dir}/{filename}"

        self.sftp.open_session()
        self.sftp.get_file(remote_dir, local_dir)
        self.sftp.close_session()

    @staticmethod
    def read_day_ahead_spot_prices_from_file(
        country: str,
        timezone: str,
        year: int,
        month: int,
        local_folder_dir: str,
    ) -> pd.DataFrame:
        """
        Reads and processes the content of the file containing day-ahead spot prices for a given
        delivery month.

        Args:
            country: Country/area of requested day-ahead spot prices
            timezone: Timezone of requested day-ahead spot prices
            year: Delivery year
            month: Delivery month
            local_folder_dir: Local directory of folder containing the price data file

        Returns:
            Dataframe containing day-ahead spot prices
        """
        # Read data from csv
        filename = Entsoe.get_sftp_filename_day_ahead_spot_prices(year=year, month=month)
        file_dir = f"{local_folder_dir}/{filename}"
        df = pd.read_csv(file_dir, sep="\t")

        # Filter columns
        columns = ["DateTime(UTC)", "ResolutionCode", "MapCode", "Price[Currency/MWh]", "Currency"]
        df = df[columns]

        # Filter rows for relevant country
        idx = df["MapCode"] == country
        df = df.loc[idx, :]
        df.reset_index(drop=True, inplace=True)

        # Convert dates from strings to datetime
        df["DateTime(UTC)"] = pd.to_datetime(
            df["DateTime(UTC)"], format="%Y-%m-%d %H:%M:%S", utc=True
        )

        # Convert from UTC timezone to local timezone
        df["DateTime(UTC)"] = df["DateTime(UTC)"].dt.tz_convert(timezone)
        df["DateTime(UTC)"] = df["DateTime(UTC)"].dt.tz_localize(None)

        return df

    def get_day_ahead_spot_prices_from_sftp(
        self, country: str, timezone: str, year: int, month: int, keep_local_file: bool = False
    ) -> pd.DataFrame:
        """
        Main method to fetch and process day-ahead spot price data from the ENSTOE SFTP server.

        The function performs the following steps:
        1) Download the file containing day-ahead spot prices from the SFTP to a temporary local
            directory.
        2) Read, process and store the price data into a dataframe.
        3) Delete the temporary local directory containing the downloaded file, unless the user
            indicates that the file should be kept.

        Args:
            country: Country/area of requested day-ahead spot prices
            timezone: Timezone of requested day-ahead spot prices
            year: Delivery year
            month: Delivery month
            keep_local_file: Indicates whether the downloaded data file should be kept or not

        Returns:
            Dataframe containing day-ahead spot prices
        """
        # Define local directory where price data file will be stored
        input_folder_dir = Path.cwd().joinpath("Inputs")
        entsoe_data_folder_dir = input_folder_dir.joinpath("EntsoeData")

        # Check if folders already exist
        input_folder_exists = input_folder_dir.exists()
        entsoe_data_folder_exists = entsoe_data_folder_dir.exists()

        # Create local directory if it doesn't exist
        entsoe_data_folder_dir.mkdir(parents=True, exist_ok=True)
        entsoe_data_folder_dir = str(entsoe_data_folder_dir)

        # Import price data file from ENTSOE SFTP to local directory
        self.import_day_ahead_spot_prices_file_from_sftp(
            year=year, month=month, local_folder_dir=entsoe_data_folder_dir
        )

        # Read price data file
        df = self.read_day_ahead_spot_prices_from_file(
            country=country,
            timezone=timezone,
            year=year,
            month=month,
            local_folder_dir=entsoe_data_folder_dir,
        )

        # Delete price data file
        if not keep_local_file:
            if input_folder_exists and entsoe_data_folder_exists:
                # Local directory already existed. Only delete the price data file.
                filename = Entsoe.get_sftp_filename_day_ahead_spot_prices(year=year, month=month)
                file_dir = Path(entsoe_data_folder_dir).joinpath(filename)
                file_dir.unlink()
            elif input_folder_exists:
                # Only the Inputs folder already existed. Delete the EntsoeData folder and its
                # content.
                shutil.rmtree(entsoe_data_folder_dir)
            else:
                # The entire temporary local directory did not exist. Delete the entire directory.
                shutil.rmtree(input_folder_dir)

        return df
