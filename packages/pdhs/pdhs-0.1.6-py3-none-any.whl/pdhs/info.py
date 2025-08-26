from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetInfo(DHSBaseAPI):
    """
    Class to fetch information from the DHS API.

    Args:
        info_type (str): Type of information to retrieve (e.g., "version", "citation").

    Returns:
        DataFrame: A polars DataFrame containing the requested information.

    Example:
    ```python
        from pdhs.info import GetInfo
        get_info = GetInfo(info_type="citation")
        df = get_info.get_data()
        print(df)
    ```
    """
    _url_extension: str = "info"
    info_type: str = "version"

    def __init__(self, info_type: str = None):
        # Explicitly initialize only the attributes you want to expose
        self.info_type = info_type
        # Pass the required _url_extension to the base class
        super().__init__(_url_extension=self._url_extension)

    def __post_init__(self):
        super().__post_init__()
        self.url = f"http://api.dhsprogram.com/rest/dhs/info?infoType={self.info_type}"

"""
get_info = GetInfo(
    info_type = "citation"
)

df = get_info.get_data()
print(df)"""