from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetTags(DHSBaseAPI):
    """
    Class to fetch tags from the DHS API.

    Args:
        indicator_ids (list): List of indicator IDs to filter the data.
        survey_ids (list): List of survey IDs to filter the data.
        survey_year (list): List of survey years to filter the data.
        survey_year_start (list): List of survey year start dates to filter the data.
        survey_year_end (list): List of survey year end dates to filter the data.
        survey_type (list): List of survey types to filter the data.
        survey_characteristics_ids (list): List of survey characteristics IDs to filter the data.
        tagIds (list): List of tag IDs to filter the data.

    Returns:
        DataFrame: A polars DataFrame containing the tags data.
    
    Example:
    ```python
        from pdhs.tags import GetTags
        Tags_data = GetTags(indicator_ids=["FE_FRTR_W_TFR"])
        df = Tags_data.get_data()
        print(df)   
    ```
    """
    _url_extension: str = "tags"


"""Tags_data = GetTags(
    indicator_ids=["FE_FRTR_W_TFR"]
)

df = Tags_data.get_data()
print(df)"""