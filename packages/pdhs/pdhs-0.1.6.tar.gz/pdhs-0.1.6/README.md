# pdhs

## Motivation

Access to high-quality, structured, and timely demographic and health data is essential for researchers, policymakers, and public health professionals. The [Demographic and Health Surveys (DHS) Program](https://www.dhsprogram.com) provides a rich repository of standardized datasets across countries and years. However, accessing and using this data programmatically can be cumbersome due to inconsistencies in interfaces, authentication requirements, and data formatting.

The `pdhs` Python library aims to streamline and simplify interaction with the DHS API. It offers an intuitive, well-documented, and Pythonic interface for querying, retrieving, and managing DHS datasets. By abstracting low-level API complexities, `pdhs` allows users to focus on analysis and application rather than on data wrangling. It supports reproducible research, integrates smoothly with common data science workflows (e.g., pandas, numpy, matplotlib), and promotes broader usage of DHS data in academic, development, and policy contexts.

> In short, `pdhs` bridges the gap between powerful public data and the tools needed to derive meaningful insights from it.

---

`pdhs` is a package for managing and analyzing [Demographic and Health Survey (DHS)](https://www.dhsprogram.com) data. It provides functionality to:

1. Access standard indicator data (via [DHS STATcompiler](https://www.statcompiler.com)) using the [DHS API](https://api.dhsprogram.com/).
2. Identify surveys and datasets relevant to specific analyses.
3. Download survey datasets from the [DHS website](https://dhsprogram.com/data/available-datasets.cfm).
4. Load datasets and associated metadata into Python.
5. Extract variables and combine datasets for pooled multi-survey analyses.

## Installation

Install the latest version from [PyPI](https://pypi.org/) using:

```bash
pip install pdhs
```

> **Note:** To download datasets from DHS, you must also install Playwright:
>
> ```bash
> playwright install
> ```

---

## Getting Started

To **download survey datasets**, you must first [create an account with DHS](https://dhsprogram.com/data/Access-Instructions.cfm) and request access. You’ll need the **email**, **password**, and **project name** associated with your DHS account when using `pdhs`.

* Request dataset access [here](https://dhsprogram.com/data/Access-Instructions.cfm)

---

## Basic Functionality

### Query the [DHS API](https://api.dhsprogram.com)

The example below retrieves Total Fertility Rate estimates for Albanian women in the **middle** and **second** wealth quintiles, categorized by **region**:

```python
from pdhs.indicators import GetIndicatorsData

indicators_data = GetIndicatorsData(
    country_ids=["AL"],
    characteristic_category=["wealth quintile", "region"],
    characteristic_label=["middle", "second"],
    breakdown="all"
)

fertility = indicators_data.get_data()
print(fertility.head())
```

<details>
<summary>Sample Output</summary>

```text
shape: (5, 28)
┌─────────┬───────────┬─────────────┬─────────────┬───┬────────┬─────────┬─────────────┬───────────┐
│ DataId  ┆ SurveyId  ┆ Indicator   ┆ IsPreferred ┆ … ┆ CIHigh ┆ IsTotal ┆ ByVariableI ┆ LevelRank │
│ ---     ┆ ---       ┆ ---         ┆ ---         ┆   ┆ ---    ┆ ---     ┆ d           ┆ ---       │
│ i64     ┆ str       ┆ str         ┆ i64         ┆   ┆ str    ┆ i64     ┆ ---         ┆ str       │
│         ┆           ┆             ┆             ┆   ┆        ┆         ┆ i64         ┆           │
╞═════════╪═══════════╪═════════════╪═════════════╪═══╪════════╪═════════╪═════════════╪═══════════╡
│ 3361769 ┆ AL2008DHS ┆ Age         ┆ 1           ┆ … ┆        ┆ 0       ┆ 0           ┆           │
│         ┆           ┆ specific    ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ fertility   ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ rate: 1…    ┆             ┆   ┆        ┆         ┆             ┆           │
│ 3419763 ┆ AL2008DHS ┆ Age         ┆ 1           ┆ … ┆        ┆ 0       ┆ 0           ┆           │
│         ┆           ┆ specific    ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ fertility   ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ rate: 1…    ┆             ┆   ┆        ┆         ┆             ┆           │
│ 3361770 ┆ AL2008DHS ┆ Age         ┆ 1           ┆ … ┆        ┆ 0       ┆ 0           ┆           │
│         ┆           ┆ specific    ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ fertility   ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ rate: 1…    ┆             ┆   ┆        ┆         ┆             ┆           │
│ 3419764 ┆ AL2008DHS ┆ Age         ┆ 1           ┆ … ┆        ┆ 0       ┆ 0           ┆           │
│         ┆           ┆ specific    ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ fertility   ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ rate: 1…    ┆             ┆   ┆        ┆         ┆             ┆           │
│ 3361764 ┆ AL2008DHS ┆ Age         ┆ 1           ┆ … ┆        ┆ 0       ┆ 0           ┆           │
│         ┆           ┆ specific    ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ fertility   ┆             ┆   ┆        ┆         ┆             ┆           │
│         ┆           ┆ rate: 2…    ┆             ┆   ┆        ┆         ┆             ┆           │
└─────────┴───────────┴─────────────┴─────────────┴───┴────────┴─────────┴─────────────┴───────────┘│
...
```

</details>


### Download Datasets

To dowload DHS datasets using `pdhs`, you need to generate a dataframe using the `GetDatasets()` class specifying the country, and file format you want to download. 

To determine which datasets to download, refer to the DHS website or use filtering options provided by the library.

---
> **Recommendation:**
>
> * Use `fileFormat = "SV"` for SPSS (.sav) — slower but fully reliable
> * Use `fileFormat = "FL"` for flat (.dat) files — faster, but a few old datasets may not load correctly
---

```python

from pdhs.datasets import GetDatasets

data = GetDatasets(
    country_ids=["NG"],
    file_format="DT"
)


df = data.get_data()
```

<details>
<summary>Sample Output</summary>

```text
shape: (5, 13)
┌───────────────┬──────────┬─────────────────┬───────────┬───┬────────────┬─────────────────┬──────────────┬─────────────┐
│ FileFormat    ┆ FileSize ┆ DatasetType     ┆ SurveyNum ┆ … ┆ SurveyYear ┆ DHS_CountryCode ┆ FileName     ┆ CountryName │
│ ---           ┆ ---      ┆ ---             ┆ ---       ┆   ┆ ---        ┆ ---             ┆ ---          ┆ ---         │
│ str           ┆ i64      ┆ str             ┆ i64       ┆   ┆ str        ┆ str             ┆ str          ┆ str         │
╞═══════════════╪══════════╪═════════════════╪═══════════╪═══╪════════════╪═════════════════╪══════════════╪═════════════╡
│ Stata dataset ┆ 2563446  ┆ Survey Datasets ┆ 32        ┆ … ┆ 1990       ┆ NG              ┆ NGBR21dt.zip ┆ Nigeria     │
│ (.dta)        ┆          ┆                 ┆           ┆   ┆            ┆                 ┆              ┆             │
│ Stata dataset ┆ 505235   ┆ Survey Datasets ┆ 32        ┆ … ┆ 1990       ┆ NG              ┆ NGHR21DT.ZIP ┆ Nigeria     │
│ (.dta)        ┆          ┆                 ┆           ┆   ┆            ┆                 ┆              ┆             │
│ Stata dataset ┆ 76104    ┆ Survey Datasets ┆ 32        ┆ … ┆ 1990       ┆ NG              ┆ NGHW21DT.ZIP ┆ Nigeria     │
│ (.dta)        ┆          ┆                 ┆           ┆   ┆            ┆                 ┆              ┆             │
│ Stata dataset ┆ 3216090  ┆ Survey Datasets ┆ 32        ┆ … ┆ 1990       ┆ NG              ┆ NGIR21DT.ZIP ┆ Nigeria     │
│ (.dta)        ┆          ┆                 ┆           ┆   ┆            ┆                 ┆              ┆             │
│ Stata dataset ┆ 2067840  ┆ Survey Datasets ┆ 32        ┆ … ┆ 1990       ┆ NG              ┆ NGKR21DT.ZIP ┆ Nigeria     │
│ (.dta)        ┆          ┆                 ┆           ┆   ┆            ┆                 ┆              ┆             │
└───────────────┴──────────┴─────────────────┴───────────┴───┴────────────┴─────────────────┴──────────────┴─────────────┘
```
</details>

Once access has been granted, use the `DHSDownloader()` and pass a list of the datasets you are interested in downloading using the `.download_all_datasets()` method. 

```python
import os
import asyncio
from dotenv import load_dotenv
from pdhs.download import DHSDownloader

load_dotenv()

dhs_password = os.getenv("DHS_PASSWORD")

downloader = DHSDownloader(
    email="<YOUR-DHS-EMAIL>",
    password="<YOUR-DHS-PASSWORD>",
    download_path="my_files",
    project_name="Rural and Urban",
    dataframe=df
)

dataset_ids = ['NGHW21DT.ZIP', 'NGBR21dt.zip', 'NGKR21DT.ZIP']

await downloader.download_all_datasets(dataset_ids)
```

> ✅ **Tips:**
>
> * Use `.env` variables to store credentials securely.
> * Change the `download_path` argument to set your preferred download folder.

> **Note:** 
>
> * The `DHSDownloader()` class takes an argument `dataframe` which is a dataset derived from the `GetDatasets()` class. You have to pass the list of datasets you are interested into the `.download_all_datasets()` class to download them.

---

### Load Downloaded Data

After downloading, load a dataset into memory as a Polars DataFrame:

```python
dataset_id = 'NGHW21DT.ZIP'  # Example ZIP dataset
df_loaded = downloader.load_dataset_as_dataframe(dataset_id)
```

<details>
<summary>Sample Output</summary>

```text

Downloading dataset: NGHW21DT.ZIP
Country Name: Nigeria
Country Code: NG
Survey ID: 32
File downloaded successfully and saved to my_files/NGHW21DT.ZIP
Downloading dataset: NGBR21dt.zip
Country Name: Nigeria
Country Code: NG
Survey ID: 32
File downloaded successfully and saved to my_files/NGBR21dt.zip
Downloading dataset: NGKR21DT.ZIP
Country Name: Nigeria
Country Code: NG
Survey ID: 32
File downloaded successfully and saved to my_files/NGKR21DT.ZIP
Extracted NGHW21DT.ZIP to my_files
Selected file for loading: my_files/NGHW21FL.DTA
Dataset NGHW21DT.ZIP loaded successfully.
shape: (5, 7)
┌─────────────────┬────────┬─────────┬──────┬──────┬──────┬──────┐
│ hwcaseid        ┆ hwline ┆ hwlevel ┆ hc70 ┆ hc71 ┆ hc72 ┆ hc73 │
│ ---             ┆ ---    ┆ ---     ┆ ---  ┆ ---  ┆ ---  ┆ ---  │
│ str             ┆ i64    ┆ i64     ┆ i64  ┆ i64  ┆ i64  ┆ i64  │
╞═════════════════╪════════╪═════════╪══════╪══════╪══════╪══════╡
│       101 11  2 ┆ 1      ┆ 2       ┆ -74  ┆ -10  ┆ 34   ┆ 47   │
│       101 11  2 ┆ 2      ┆ 2       ┆ -67  ┆ 6    ┆ 58   ┆ 68   │
│       101 19  2 ┆ 1      ┆ 2       ┆ null ┆ null ┆ null ┆ null │
│       101 19  2 ┆ 2      ┆ 2       ┆ null ┆ null ┆ null ┆ null │
│       101 39  2 ┆ 1      ┆ 2       ┆ -258 ┆ -138 ┆ 58   ┆ 20   │
└─────────────────┴────────┴─────────┴──────┴──────┴──────┴──────┘
```

</details>

---

### Convert to Pandas (Optional)

By default, `pdhs` returns data as [Polars](https://pola.rs) DataFrames for performance. You can easily convert to Pandas:

```python
import pandas as pd

df = df_loaded.to_pandas()
df.head()

```

<details>
<summary>Sample Output</summary>

```text

hwcaseid	hwline	hwlevel	hc70	hc71	hc72	hc73
0	101 11 2	1	2	-74.0	-10.0	34.0	47.0
1	101 11 2	2	2	-67.0	6.0	58.0	68.0
2	101 19 2	1	2	NaN	NaN	NaN	NaN
3	101 19 2	2	2	NaN	NaN	NaN	NaN
4	101 39 2	1	2	-258.0	-138.0	58.0	20.0

```

</details>

---


