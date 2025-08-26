import polars as pl
import logging
from dataclasses import field, dataclass
from typing import List
from .base_api import DHSBaseAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class GetIndicatorsData(DHSBaseAPI):
    """
    Class to fetch indicators data from the DHS API.

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
        characteristic_category (list): List of characteristic categories to filter the data.
        characteristic_label (list): List of characteristic labels to filter the data.
        breakdown (str): Breakdown type for the indicators.

    Returns:
        DataFrame: A polars DataFrame containing the indicators data.

    Example:
    ```python
        from pdhs.indicators import GetIndicatorsData
        indicators_data = GetIndicatorsData(
            country_ids=["AL"],
            characteristic_category=["wealth quintile", "region"],
            characteristic_label=["middle", "second"],
            breakdown="all"
        )
        df = indicators_data.get_data()
        print(df)
    ```
    """
    _url_extension: str = "data"
    characteristic_category: List[str] = field(default_factory=list)
    characteristic_label: List[str] = field(default_factory=list)
    breakdown: str = ""

    @staticmethod
    def _convert_special_characters(input_string: str) -> str:
        """
        Converts spaces in a string to '%20' and '+' to '%2B'.
        
        Args:
            input_string (str): The input string to be converted.
        
        Returns:
            str: The converted string with spaces replaced by '%20' and '+' replaced by '%2B'.
        """
        return input_string.replace(" ", "%20").replace("+", "%2B")

    def __post_init__(self):
        super().__post_init__()
        # Apply _convert_special_characters to each string in characteristic_category
        self.characteristic_category = [
            self._convert_special_characters(cat) for cat in self.characteristic_category
        ]
        self.characteristic_label = [
            self._convert_special_characters(label) for label in self.characteristic_label
        ]
        self.url += (f"&characteristicCatrgory={self._convert_query_list_to_string(self.characteristic_category)}"
                    f"&characteristicLabel={self._convert_query_list_to_string(self.characteristic_label)}"
                    f"&breakdown={self.breakdown}")
        logging.info(f"Extended API URL constructed: {self.url}")

@dataclass
class GetIndicators(DHSBaseAPI):
    _url_extension: str = "indicators"


"""# Example usage
indicators_data = GetIndicatorsData(
    country_ids = ["AL"],
    characteristic_category=["wealth quintile", "region"],
    characteristic_label=["middle", "second"],
    breakdown="all"
)


df = indicators_data.get_data()
print(df)

#df.columns

# Example usage
indicators = GetIndicators(
    indicator_ids = ["FE_FRTR_W_TFR"],
)


df2 = indicators.get_data()
print(df2)

#df2.columns
"""