import polars as pl
import logging
from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetSurveys(DHSBaseAPI):
    """
    Class to fetch survey data from the DHS API.

    Args:
        country_ids (list): List of country IDs to filter the data.
        survey_status (str): Status of the surveys to filter (e.g., "completed", "ongoing").
        indicator_ids (list): List of indicator IDs to filter the data.
        survey_ids (list): List of survey IDs to filter the data.
        survey_year (list): List of survey years to filter the data.
        survey_year_start (list): List of survey year start dates to filter the data.
        survey_year_end (list): List of survey year end dates to filter the data.
        survey_type (list): List of survey types to filter the data.
        survey_characteristics_ids (list): List of survey characteristics IDs to filter the data.
        tagIds (list): List of tag IDs to filter the data.
    
    Returns:
        DataFrame: A polars DataFrame containing the survey data.
    
    Example:
    ```python
        from pdhs.surveys import GetSurveys
        survey_data = GetSurveys(
            country_ids=["NG"],
            survey_status="completed",
        )
        df = survey_data.get_data()
        print(df)   
    ```
    """
    _url_extension: str = "surveys"
    survey_status: str = None
    

    def __post_init__(self):
        super().__post_init__()
        if self.survey_status is not None:
            self.url += (f"&surveyStatus={self.survey_status}")
        logging.info(f"Extended API URL constructed: {self.url}")

@dataclass
class GetSurveyCharacteristics(DHSBaseAPI):
    _url_extension: str = "surveycharacteristics"

"""survey_data = GetSurveys(
    country_ids=["NG"],
    survey_status="completed",
)
df = survey_data.get_data()
print(df)

survey_xtics = GetSurveyCharacteristics(
    country_ids=["NG"],
    survey_year = ["2018"],
    survey_ids = ["DHS-2018"],
)
df2 = survey_xtics.get_data()
print(df2)"""