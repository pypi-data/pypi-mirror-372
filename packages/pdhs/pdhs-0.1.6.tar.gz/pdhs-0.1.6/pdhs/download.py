import polars as pl
from dataclasses import dataclass
from playwright.async_api import async_playwright
from typing import Optional
import requests
import os
import zipfile
import pyreadstat
import asyncio

from .datasets import GetDatasets


@dataclass
class DHSDownloader:
    """
    A class to handle downloading datasets from the Demographic and Health Surveys (DHS) Program.

    This class provides methods to authenticate with the DHS API, search for available datasets,
    and download selected datasets to a specified directory.

    Requires Playwright for browser automation and requests for HTTP requests.

    Args:
        username (str): DHS API username.
        password (str): DHS API password.
        download_dir (str): Directory where datasets will be saved.
        project_name (str): Name of the project to select from the DHS dropdown.
        dataframe (pl.DataFrame): Polars DataFrame containing dataset metadata.

    Methods:
        download_all_datasets(dataset_ids: list): Downloads all datasets specified by their IDs.
        load_dataset_as_dataframe(dataset_id: str): Loads a downloaded dataset into a Polars DataFrame.

    Example:
    ```python
        from pdhs.download import DHSDownloader
        downloader = DHSDownloader(
            email="example@email.com",
            password="your_password",
            project_name="Your Project Name",
            dataframe=GetDatasets(country_ids=["NG"], file_format="DT").get_data()
    ```
    """

    email: str
    password: str
    project_name: str
    dataframe: pl.DataFrame
    download_path: Optional[str] = None

    def __post_init__(self):
        if self.download_path is None:
            self.download_path = "downloads"

    async def download_all_datasets(self, dataset_ids: list):
        """
        Iterates over the provided dataset IDs and downloads each dataset.
        Args:
            dataset_ids (list): List of dataset IDs to download.
        """
        for dataset_id in dataset_ids:
            try:
                await self._download_single_dataset(dataset_id)
            except ValueError as e:
                print(f"Skipping dataset {dataset_id} due to error: {e}")

    async def _download_single_dataset(self, dataset_id: str):
        """
        Downloads a single dataset by filtering the dataframe and automating the download process.
        """
        # Automatically determine the FileName column
        file_name_column = "FileName"
        if file_name_column not in self.dataframe.columns:
            raise ValueError(f"Column '{file_name_column}' not found in the provided dataframe.")

        # Filter the dataframe for the current dataset_id
        filtered_df = self.dataframe.filter(pl.col(file_name_column) == dataset_id)

        # Extract values from the filtered dataframe
        if filtered_df.is_empty():
            raise ValueError(f"No data found for dataset_id: {dataset_id}")

        country_name = filtered_df['CountryName'][0]
        country_code = filtered_df['DHS_CountryCode'][0]
        survey_id = filtered_df['SurveyNum'][0]

        # Print extracted values (optional)
        print(f"Downloading dataset: {dataset_id}")
        print(f"Country Name: {country_name}")
        print(f"Country Code: {country_code}")
        print(f"Survey ID: {survey_id}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            # Navigate to the DHS login page
            await page.goto("https://dhsprogram.com/data/dataset_admin/login_main.cfm")

            # Fill in the login form
            await page.fill("input[name='UserName']", self.email)
            await page.fill("input[name='UserPass']", self.password)

            # Submit the login form
            await page.click("input[type='submit']")

            # Wait for navigation after login
            await page.wait_for_load_state("networkidle")

            # Select the project from the dropdown
            await page.select_option("select[name='proj_id']", label=self.project_name)

            # Wait for the project selection to complete
            await page.wait_for_load_state("networkidle")

            # Extract cookies from Playwright
            cookies = await context.cookies()
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            # Directly download the dataset using the provided URL
            download_url = f"https://dhsprogram.com/customcf/legacy/data/download_dataset.cfm?Filename={dataset_id}&Tp=1&Ctry_Code={country_code}&surv_id={survey_id}&dm=1&dmode=nm"
            save_path = f"{self.download_path}/{dataset_id}"
            self._download_file_with_session(session, download_url, save_path)

            # Close the browser
            await browser.close()

    @staticmethod
    def _download_file_with_session(session, url, save_path):
        """
        Downloads a file using a session with cookies and saves it to the specified path.

        Args:
            session (requests.Session): The session with cookies.
            url (str): The URL of the file to download.
            save_path (str): The local path where the file will be saved.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            response = session.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"File downloaded successfully and saved to {save_path}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def load_dataset_as_dataframe(self, dataset_id: str) -> pl.DataFrame:
        """
        Loads a downloaded dataset into a Polars DataFrame.

        Args:
            dataset_id (str): The ID of the dataset to load.

        Returns:
            pl.DataFrame: The dataset loaded as a Polars DataFrame.
        """
        file_path = f"{self.download_path}/{dataset_id}"
        try:
            # Check if the file is a ZIP file
            if file_path.lower().endswith(".zip"):
                # Extract the ZIP file
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.download_path)
                    print(f"Extracted {dataset_id} to {self.download_path}")

                # Find all extracted files
                extracted_files = [
                    f for f in os.listdir(self.download_path)
                    if os.path.isfile(os.path.join(self.download_path, f)) and not f.endswith(".zip")
                ]

                # Filter files by supported extensions
                supported_extensions = ["csv", "dat", "dta", "sas7bdat", "sav"]
                extracted_files = [
                    f for f in extracted_files
                    if f.split('.')[-1].lower() in supported_extensions
                ]

                if not extracted_files:
                    raise FileNotFoundError(f"No supported files found after extracting {dataset_id}")

                # Select the first supported file (or implement custom logic to choose)
                file_path = os.path.join(self.download_path, extracted_files[0])
                print(f"Selected file for loading: {file_path}")

            # Determine the file extension
            file_extension = file_path.split('.')[-1].lower()

            if file_extension == "csv" or file_extension == "dat":
                # Load CSV or DAT files using Polars
                df = pl.read_csv(file_path)
            elif file_extension == "dta":
                # Load Stata files using pyreadstat
                df, meta = pyreadstat.read_dta(file_path)
                df = pl.DataFrame(df)  # Convert pandas DataFrame to Polars DataFrame
            elif file_extension == "sas7bdat":
                # Load SAS files using pyreadstat
                df, meta = pyreadstat.read_sas7bdat(file_path)
                df = pl.DataFrame(df)  # Convert pandas DataFrame to Polars DataFrame
            elif file_extension == "sav":
                # Load SPSS files using pyreadstat
                df, meta = pyreadstat.read_sav(file_path)
                df = pl.DataFrame(df)  # Convert pandas DataFrame to Polars DataFrame
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            print(f"Dataset {dataset_id} loaded successfully.")
            return df
        except FileNotFoundError:
            print(f"Dataset {dataset_id} not found in {self.download_path}.")
        except Exception as e:
            print(f"An error occurred while loading the dataset: {e}")

"""# Main execution function
async def main():
    # Example usage
    indicators_data = GetDatasets(
        country_ids=["NG"],
        file_format="DT"
    )

    df = indicators_data.get_data()
    print(df)

    downloader = DHSDownloader(
        email="adejumo999@gmail.com",
        password=dhs_password,
        download_path="my_files",
        project_name="Rural and Urban",
        dataframe=df
    )

    dataset_ids = ['NGHW21DT.ZIP', 'NGBR21dt.zip', 'NGKR21DT.ZIP']
    await downloader.download_all_datasets(dataset_ids)

    # After downloading datasets
    dataset_id = 'NGHW21DT.ZIP'  # Example ZIP dataset
    df_loaded = downloader.load_dataset_as_dataframe(dataset_id)

    # Perform operations on the loaded DataFrame
    if df_loaded is not None:
        print(df_loaded.head())

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())"""