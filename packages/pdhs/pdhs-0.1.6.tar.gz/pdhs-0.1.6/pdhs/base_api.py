import requests
import polars as pl
import logging
from dataclasses import dataclass, field
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class DHSBaseAPI:

    """
    Base Class to fetch data from the DHS API.
    
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

    """
    _url_extension: str
    country_ids: List[str] = field(default_factory=list)
    indicator_ids: List[str] = field(default_factory=list)
    survey_ids: List[str] = field(default_factory=list)
    survey_year: List[str] = field(default_factory=list)
    survey_year_start: List[str] = field(default_factory=list)
    survey_year_end: List[str] = field(default_factory=list)
    survey_type: List[str] = field(default_factory=list)
    survey_characteristics_ids: List[str] = field(default_factory=list)
    tagIds: List[str] = field(default_factory=list)
    filter_fields: List[str] = field(default_factory=list)  # Fields to filter
    _timeout: int = 10  # Request timeout in seconds


    def __post_init__(self):
        """Construct the API URL after initialization."""
        self.url = (
            f"http://api.dhsprogram.com/rest/dhs/{self._url_extension}?"
            f"surveyYears={self._convert_query_list_to_string(self.survey_year)}&"
            f"countryIds={self._convert_query_list_to_string(self.country_ids)}&"
            f"indicatorIds={self._convert_query_list_to_string(self.indicator_ids)}&"
            f"surveyYearIds={self._convert_query_list_to_string(self.survey_ids)}&"
            f"surveyYearStarts={self._convert_query_list_to_string(self.survey_year_start)}&"
            f"surveyYearEnds={self._convert_query_list_to_string(self.survey_year_end)}&"
            f"surveyTypes={self._convert_query_list_to_string(self.survey_type)}&"
            f"surveyCharacteristicsIds={self._convert_query_list_to_string(self.survey_characteristics_ids)}&"
            f"tagIds={self._convert_query_list_to_string(self.tagIds)}"
        )
        logging.info(f"API URL constructed: {self.url}")

    @staticmethod
    def _convert_query_list_to_string(query_list: List[str]) -> str:
        """Convert a list of values into a comma-separated string."""
        return ",".join(query_list) if query_list else ""

    def _fetch_data(self) -> List[dict]:
        """Fetch survey data from the API with error handling."""
        try:
            response = requests.get(self.url, timeout=self._timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx, 5xx)
            data = response.json().get("Data", [])
            
            if not data:
                logging.warning("API response is empty or missing 'Data' key.")
            return data
        except requests.Timeout:
            logging.error("Request timed out.")
            return []
        except requests.HTTPError as e:
            logging.error(f"HTTP error occurred: {e}")
            return []
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return []
        except ValueError:
            logging.error("Error decoding JSON response.")
            return []

    @staticmethod
    def _convert_data_to_polars(data: List[dict]) -> Optional[pl.DataFrame]:
        """Convert JSON data to a Polars DataFrame, handling empty data cases."""
        try:
            if not data:
                logging.warning("No data available to convert to DataFrame.")
                return None
            return pl.DataFrame(data)
        except Exception as e:
            logging.error(f"Error converting data to Polars DataFrame: {e}")
            return None

    def _select_columns(self, data: pl.DataFrame) -> Optional[pl.DataFrame]:
        """Select specific columns if filter_fields is provided."""
        if not self.filter_fields:
            return data  # Return full DataFrame if no filters are provided
        
        try:
            # Ensure requested columns exist
            available_columns = set(data.columns)
            missing_columns = set(self.filter_fields) - available_columns
            if missing_columns:
                logging.warning(f"Skipping missing columns: {missing_columns}")

            selected_columns = [col for col in self.filter_fields if col in available_columns]
            return data.select(selected_columns)
        except Exception as e:
            logging.error(f"Error selecting columns: {e}")
            return None

    def get_data(self) -> Optional[pl.DataFrame]:
        """
        Public method to return the final processed DataFrame.

        Returns:
            Optional[pl.DataFrame]: Polars DataFrame or None if an error occurs.
        """
        raw_data = self._fetch_data()
        df = self._convert_data_to_polars(raw_data)
        if df is None:
            return None
        return self._select_columns(df)


"""#Example usage
survey_data = DHSBaseAPI(
    country_ids = ["NG", "GH"],
    filter_fields=[],
    url_extension = "countries"
)


df_s = survey_data.get_data()
print(df_s)
"""