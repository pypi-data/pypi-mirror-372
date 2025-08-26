import polars as pl
import logging
from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetPublications(DHSBaseAPI):
    """
    Class to fetch publications from the DHS API.

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

    Returns:
        DataFrame: A polars DataFrame containing the publications data.

    Example:
    ```python
        from pdhs.publications import GetPublications
        get_publications = GetPublications(country_ids=["AL"])
        df = get_publications.get_data()
        print(df)
    ```
    """
    _url_extension: str = "publications"


"""get_publications = GetPublications(
    country_ids=["AL"],
)

df = get_publications.get_data()
print(df)"""