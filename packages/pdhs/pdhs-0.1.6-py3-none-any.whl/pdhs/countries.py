from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetCountries(DHSBaseAPI):
    """
    Class to fetch country data from the DHS API.

    Inherits from DHSBaseAPI and uses the 'countries' endpoint.

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
        DataFrame: A polars DataFrame containing the country data.

    Example:
    ```python
        from pdhs.countries import GetCountries
        countries_data = GetCountries(country_ids = ["AL"])
        df = countries_data.get_data()
        print(df)
    ```
    """
    _url_extension: str = "countries"


"""
countries_data = GetCountries(
    country_ids = ["AL"]
)

df = countries_data.get_data()
print(df)
"""