import pytest
from unittest.mock import patch, MagicMock, mock_open
import polars as pl
import os
import zipfile
import requests
from pdhs.download import DHSDownloader

from dotenv import load_dotenv
load_dotenv()

dhs_password = os.getenv("DHS_PASSWORD")

class TestDHSDownloader:
    
    def setup_method(self):
        """Setup test data and DHSDownloader instance."""
        self.test_df = pl.DataFrame({
            "FileName": ["NGHW21DT.ZIP", "NGBR21dt.zip", "NGKR21DT.ZIP"],
            "CountryName": ["Nigeria", "Nigeria", "Nigeria"],
            "DHS_CountryCode": ["NG", "NG", "NG"],
            "SurveyNum": ["21", "21", "21"]
        })
        
        self.downloader = DHSDownloader(
            email="adejumo999@gmail.com",
            password=dhs_password,
            download_path="test_downloads",
            project_name="Rural and Urban",
            dataframe=self.test_df
        )

    def test_initialization(self):
        """Test DHSDownloader initialization."""
        assert self.downloader.email == "adejumo999@gmail.com"
        assert self.downloader.password == dhs_password
        assert self.downloader.download_path == "test_downloads"
        assert self.downloader.project_name == "Rural and Urban"
        assert self.downloader.dataframe.equals(self.test_df)

    @patch.object(DHSDownloader, '_download_single_dataset')
    def test_download_all_datasets_success(self, mock_download):
        """Test successful download of all datasets."""
        dataset_ids = ['NGHW21DT.ZIP', 'NGBR21dt.zip']
        
        self.downloader.download_all_datasets(dataset_ids)
        
        assert mock_download.call_count == 2
        mock_download.assert_any_call('NGHW21DT.ZIP')
        mock_download.assert_any_call('NGBR21dt.zip')

    @patch.object(DHSDownloader, '_download_single_dataset')
    @patch('builtins.print')
    def test_download_all_datasets_with_errors(self, mock_print, mock_download):
        """Test download_all_datasets handles errors gracefully."""
        dataset_ids = ['NGHW21DT.ZIP', 'INVALID.ZIP']
        mock_download.side_effect = [None, ValueError("Test error")]
        
        self.downloader.download_all_datasets(dataset_ids)
        
        mock_print.assert_called_with("Skipping dataset INVALID.ZIP due to error: Test error")

    def test_download_single_dataset_missing_column(self):
        """Test _download_single_dataset with missing FileName column."""
        df_no_filename = pl.DataFrame({"OtherColumn": ["value"]})
        downloader = DHSDownloader(
            email="adejumo999@gmail.com",
            password=dhs_password, 
            download_path="test_downloads",
            project_name="Rural and Urban",
            dataframe=df_no_filename
        )
        
        with pytest.raises(ValueError, match="Column 'FileName' not found"):
            downloader._download_single_dataset("NGHW21DT.ZIP")

    def test_download_single_dataset_no_data_found(self):
        """Test _download_single_dataset with dataset_id not in dataframe."""
        with pytest.raises(ValueError, match="No data found for dataset_id: NONEXISTENT.ZIP"):
            self.downloader._download_single_dataset("NONEXISTENT.ZIP")

    @patch('pdhs.download.sync_playwright')
    @patch.object(DHSDownloader, '_download_file_with_session')
    @patch('builtins.print')
    def test_download_single_dataset_success(self, mock_print, mock_download_file, mock_playwright):
        """Test successful single dataset download."""
        # Mock playwright context
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_playwright_instance = MagicMock()
        
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_context.cookies.return_value = [{'name': 'test', 'value': 'cookie'}]
        
        self.downloader._download_single_dataset("NGHW21DT.ZIP")
        
        # Verify playwright interactions
        mock_page.goto.assert_called_with("https://dhsprogram.com/data/dataset_admin/login_main.cfm")
        mock_page.fill.assert_any_call("input[name='UserName']", "adejumo999@gmail.com")
        mock_page.fill.assert_any_call("input[name='UserPass']", dhs_password)
        mock_page.click.assert_called_with("input[type='submit']")
        mock_page.select_option.assert_called_with("select[name='proj_id']", label="Rural and Urban")
        mock_browser.close.assert_called_once()
        
        # Verify download was called
        mock_download_file.assert_called_once()

    
    @patch('pdhs.download.pyreadstat.read_dta')
    @patch('builtins.print')
    def test_load_dataset_as_dataframe_dta(self, mock_print, mock_read_dta):
        """Test loading DTA file."""
        pandas_df = MagicMock()
        mock_read_dta.return_value = (pandas_df, {})
        mock_polars_df = pl.DataFrame({"col1": [1, 2]})
        
        with patch('pdhs.download.pl.DataFrame', return_value=mock_polars_df):
            result = self.downloader.load_dataset_as_dataframe("test.dta")
            
        mock_read_dta.assert_called_once()
        assert result.equals(mock_polars_df)

    @patch('pdhs.download.pyreadstat.read_sas7bdat')
    @patch('builtins.print')
    def test_load_dataset_as_dataframe_sas(self, mock_print, mock_read_sas):
        """Test loading SAS file."""
        pandas_df = MagicMock()
        mock_read_sas.return_value = (pandas_df, {})
        mock_polars_df = pl.DataFrame({"col1": [1, 2]})
        
        with patch('pdhs.download.pl.DataFrame', return_value=mock_polars_df):
            result = self.downloader.load_dataset_as_dataframe("test.sas7bdat")
            
        mock_read_sas.assert_called_once()
        assert result.equals(mock_polars_df)

    @patch('pdhs.download.pyreadstat.read_sav')
    @patch('builtins.print')
    def test_load_dataset_as_dataframe_spss(self, mock_print, mock_read_sav):
        """Test loading SPSS file."""
        pandas_df = MagicMock()
        mock_read_sav.return_value = (pandas_df, {})
        mock_polars_df = pl.DataFrame({"col1": [1, 2]})
        
        with patch('pdhs.download.pl.DataFrame', return_value=mock_polars_df):
            result = self.downloader.load_dataset_as_dataframe("test.sav")
            
        mock_read_sav.assert_called_once()
        assert result.equals(mock_polars_df)

    @patch('builtins.print')
    def test_load_dataset_as_dataframe_unsupported_format(self, mock_print):
        """Test loading unsupported file format."""
        result = self.downloader.load_dataset_as_dataframe("test.xyz")
        
        assert result is None
        mock_print.assert_any_call("An error occurred while loading the dataset: Unsupported file format: xyz")

    @patch('builtins.print')
    def test_load_dataset_as_dataframe_file_not_found(self, mock_print):
        """Test loading non-existent file."""
        result = self.downloader.load_dataset_as_dataframe("nonexistent.csv")
        
        assert result is None
        mock_print.assert_called_with("Dataset nonexistent.csv not found in test_downloads.")

    @patch('pdhs.download.pl.read_csv')
    @patch('builtins.print')
    def test_load_dataset_as_dataframe_dat_file(self, mock_print, mock_read_csv):
        """Test loading DAT file."""
        mock_df = pl.DataFrame({"col1": [1, 2]})
        mock_read_csv.return_value = mock_df
        
        result = self.downloader.load_dataset_as_dataframe("test.dat")
        
        mock_read_csv.assert_called_once()
        assert result.equals(mock_df)