import polars as pl
import logging
from dataclasses import field, dataclass
from typing import List
from .base_api import DHSBaseAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class GetDatasets(DHSBaseAPI):
    """
    Class to fetch datasets from the DHS API.

    Args:
        country_ids (list): List of country IDs to filter the data.
        indicator_ids (list): List of indicator IDs to filter the data.
        survey_ids (list): List of survey IDs to filter the data.
        survey_year (list): List of survey years to filter the data.
        survey_year_start (list): List of survey year start dates to filter the data.
        survey_year_end (list): List of survey year end dates to filter the data.
        survey_type (list): List of survey types to filter the data.
        survey_characteristics_ids (list): List of survey characteristics IDs to filter the data.
        tagIds (list): List of tag IDs to filter the data.
        filter_fields (list): List of fields to filter the data.
        select_surveys (str): Comma-separated list of survey IDs to select.
        file_format (str): Format of the files to retrieve (e.g., "DT" for data tables).
        file_type (str): Type of the files to retrieve (e.g., "CSV", "JSON").

    Returns:
        DataFrame: A polars DataFrame containing the dataset information.

    Example:
    ```python
        from pdhs.datasets import GetDatasets
        indicators_data = GetDatasets(country_ids = ["NG"], file_format = "DT")
        df = indicators_data.get_data()
        print(df)
    ```
    """
    _url_extension: str = "datasets"
    select_surveys: str = None
    file_format: str = None
    file_type: str = None

    def __post_init__(self):
        super().__post_init__()
        
        if self.select_surveys is not None:
            self.url += f"&selectSurveys={self.select_surveys}"
        if self.file_format is not None:
            self.url += f"&fileFormat={self.file_format}"
        if self.file_type is not None:
            self.url += f"&fileType={self.file_type}"
        
        logging.info(f"Extended API URL constructed: {self.url}")


"""
indicators_data = GetDatasets(
    country_ids = ["NG"],
    file_format = "DT"
)

df = indicators_data.get_data()
print(df)
"""