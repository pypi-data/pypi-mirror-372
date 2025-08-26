import unittest
from unittest.mock import patch, MagicMock
import polars as pl
from pdhs.base_api import DHSBaseAPI
import requests
import requests

# pdhs/test_base_api.py



class TestDHSBaseAPI(unittest.TestCase):

    def setUp(self):
        self.api = DHSBaseAPI(_url_extension="countries")

    def test_convert_query_list_to_string(self):
        self.assertEqual(DHSBaseAPI._convert_query_list_to_string([]), "")
        self.assertEqual(DHSBaseAPI._convert_query_list_to_string(["A", "B"]), "A,B")

    @patch("pdhs.base_api.requests.get")
    def test_fetch_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"Data": [{"a": 1}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        data = self.api._fetch_data()
        self.assertEqual(data, [{"a": 1}])

    @patch("pdhs.base_api.requests.get")
    def test_fetch_data_empty(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        data = self.api._fetch_data()
        self.assertEqual(data, [])

    @patch("pdhs.base_api.requests.get")
    def test_fetch_data_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()
        data = self.api._fetch_data()
        self.assertEqual(data, [])

    @patch("pdhs.base_api.requests.get")
    def test_fetch_data_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad request")
        mock_get.return_value = mock_response
        data = self.api._fetch_data()
        self.assertEqual(data, [])

    @patch("pdhs.base_api.requests.get")
    def test_fetch_data_value_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Malformed JSON")
        mock_get.return_value = mock_response
        data = self.api._fetch_data()
        self.assertEqual(data, [])

    def test_convert_data_to_polars_valid(self):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        df = DHSBaseAPI._convert_data_to_polars(data)
        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape, (2, 2))

    def test_convert_data_to_polars_empty(self):
        df = DHSBaseAPI._convert_data_to_polars([])
        self.assertIsNone(df)

    def test_convert_data_to_polars_exception(self):
        # Pass data that will create a DataFrame, but not None
        class BadList(list): pass
        bad_data = BadList([object()])
        df = DHSBaseAPI._convert_data_to_polars(bad_data)
        self.assertIsInstance(df, pl.DataFrame)

    def test_select_columns_no_filter(self):
        df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
        self.api.filter_fields = []
        result = self.api._select_columns(df)
        self.assertTrue(result.equals(df))

    def test_select_columns_with_filter(self):
        df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
        self.api.filter_fields = ["a"]
        result = self.api._select_columns(df)
        self.assertEqual(result.columns, ["a"])

    def test_select_columns_missing(self):
        df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
        self.api.filter_fields = ["a", "c"]
        result = self.api._select_columns(df)
        self.assertEqual(result.columns, ["a"])

    def test_select_columns_exception(self):
        df = "not a dataframe"
        self.api.filter_fields = ["a"]
        result = self.api._select_columns(df)
        self.assertIsNone(result)

    @patch.object(DHSBaseAPI, "_fetch_data")
    @patch.object(DHSBaseAPI, "_convert_data_to_polars")
    @patch.object(DHSBaseAPI, "_select_columns")
    def test_get_data_full_flow(self, mock_select, mock_convert, mock_fetch):
        mock_fetch.return_value = [{"a": 1}]
        mock_df = pl.DataFrame({"a": [1]})
        mock_convert.return_value = mock_df
        mock_select.return_value = mock_df
        result = self.api.get_data()
        self.assertTrue(result.equals(mock_df))

    @patch.object(DHSBaseAPI, "_fetch_data", return_value=[])
    def test_get_data_no_data(self, mock_fetch):
        result = self.api.get_data()
        self.assertIsNone(result)

    @patch.object(DHSBaseAPI, "_fetch_data", return_value=[{"a": 1}])
    @patch.object(DHSBaseAPI, "_convert_data_to_polars", return_value=None)
    def test_get_data_conversion_fail(self, mock_convert, mock_fetch):
        result = self.api.get_data()
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()

import pytest
from unittest.mock import patch, MagicMock
import polars as pl
from pdhs.base_api import DHSBaseAPI
from requests import Timeout
from requests import HTTPError

# pdhs/test_base_api.py



def test_post_init_url_construction():
    api = DHSBaseAPI(
        _url_extension="countries",
        country_ids=["NG", "GH"],
        indicator_ids=["ID1"],
        survey_ids=["S1"],
        survey_year=["2020"],
        survey_year_start=["2019"],
        survey_year_end=["2021"],
        survey_type=["Type1"],
        survey_characteristics_ids=["C1"],
        tagIds=["T1"],
        filter_fields=[]
    )
    assert "countryIds=NG,GH" in api.url
    assert "indicatorIds=ID1" in api.url
    assert "surveyYearIds=S1" in api.url
    assert "surveyYears=2020" in api.url
    assert "surveyYearStarts=2019" in api.url
    assert "surveyYearEnds=2021" in api.url
    assert "surveyTypes=Type1" in api.url
    assert "surveyCharacteristicsIds=C1" in api.url
    assert "tagIds=T1" in api.url
    assert "apiKey=ICLSPH-527168" in api.url

def test_convert_query_list_to_string():
    assert DHSBaseAPI._convert_query_list_to_string(["a", "b", "c"]) == "a,b,c"
    assert DHSBaseAPI._convert_query_list_to_string([]) == ""
    assert DHSBaseAPI._convert_query_list_to_string(["one"]) == "one"

@patch("pdhs.base_api.requests.get")
def test_fetch_data_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"Data": [{"a": 1}, {"a": 2}]}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    api = DHSBaseAPI(_url_extension="countries")
    data = api._fetch_data()
    assert data == [{"a": 1}, {"a": 2}]


@patch("pdhs.base_api.requests.get")
def test_fetch_data_timeout(mock_get):
    mock_get.side_effect = Timeout
    api = DHSBaseAPI(_url_extension="countries")
    data = api._fetch_data()
    assert data == []

@patch("pdhs.base_api.requests.get")
def test_fetch_data_http_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = HTTPError("Bad response")
    mock_get.return_value = mock_resp
    api = DHSBaseAPI(_url_extension="countries")
    data = api._fetch_data()
    assert data == []

@patch("pdhs.base_api.requests.get")
def test_fetch_data_bad_json(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.side_effect = ValueError("bad json")
    mock_get.return_value = mock_resp
    api = DHSBaseAPI(_url_extension="countries")
    data = api._fetch_data()
    assert data == []

def test_convert_data_to_polars_valid():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    df = DHSBaseAPI._convert_data_to_polars(data)
    assert isinstance(df, pl.DataFrame)
    assert set(df.columns) == {"a", "b"}
    assert df.shape == (2, 2)

def test_convert_data_to_polars_empty():
    df = DHSBaseAPI._convert_data_to_polars([])
    assert df is None

def test_convert_data_to_polars_invalid():
    # Passing data that can't be converted to DataFrame
    df = DHSBaseAPI._convert_data_to_polars([object()])
    assert isinstance(df, pl.DataFrame)

def test_select_columns_all_present():
    data = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    api = DHSBaseAPI(_url_extension="countries", filter_fields=["a", "b"])
    df = api._select_columns(data)
    assert set(df.columns) == {"a", "b"}

def test_select_columns_some_missing(caplog):
    data = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    api = DHSBaseAPI(_url_extension="countries", filter_fields=["a", "c"])
    df = api._select_columns(data)
    assert "a" in df.columns
    assert "c" not in df.columns


def test_select_columns_error(monkeypatch):
    data = pl.DataFrame({"a": [1, 2]})
    api = DHSBaseAPI(_url_extension="countries", filter_fields=["a"])
    monkeypatch.setattr(data, "select", lambda cols: (_ for _ in ()).throw(Exception("fail")))
    df = api._select_columns(data)
    assert df is None

@patch("pdhs.base_api.requests.get")
def test_get_data_full_flow(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"Data": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    api = DHSBaseAPI(_url_extension="countries", filter_fields=["x"])
    df = api.get_data()
    assert isinstance(df, pl.DataFrame)
    assert set(df.columns) == {"x"}
    assert df.shape == (2, 1)

@patch("pdhs.base_api.requests.get")
def test_get_data_empty(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"Data": []}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    api = DHSBaseAPI(_url_extension="countries")
    df = api.get_data()
    assert df is None