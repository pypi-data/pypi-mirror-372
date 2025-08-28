[![PyPI version](https://badge.fury.io/py/prism-pull.svg)](https://badge.fury.io/py/prism-pull)
[![codecov](https://codecov.io/gh/jtbaird/prism-pull/branch/main/graph/badge.svg)](https://codecov.io/gh/jtbaird/prism-pull)
![Build Status](https://github.com/jtbaird/prism-pull/actions/workflows/main-deploy.yml/badge.svg)
# prism-pull
prism-pull is a python package made to pull data from PRISM Group using web automation. For those not familiar with PRISM Group, via the [PRISM website](https://prism.nacse.org/):
```
The PRISM Group gathers weather observations from a wide range of monitoring networks, applies
sophisticated quality control measures, and develops spatial datasets to reveal short- and 
long-term weather patterns. The resulting datasets incorporate a variety of modeling techniques 
and are available at multiple spatial/temporal resolutions, covering the period from 1895 to 
the present. 
```
The types of weather data consist of:
- precipitaion totals
- minimum temperatures
- mean temperatures
- maximum temperatures
- minimum vapor pressure deficit
- maximum vapor pressure deficit
- mean dewpoint temperature
- cloud transmittance
- horizontal surface solar radiation data
- sloped surface solar radiation data
- clear sky solar radiation data

These data are available across a variety of timescales for each cell of a 4km by 4km or 800m by 800m grid covering the entire continential United States. This makes it an especially great source for locations where weather stations may not be operating.
## Installation
Prerequisites:
- pip
- Google Chrome
- Python3.10 or higher

Install with: `pip install prism-pull`
## Usage
Remember to follow the [PRISM Group](https://prism.nacse.org/terms/) terms of use for whatever your project may be. Usage is simple, and will be familiar to anyone who has used the PRISM GUI in the past. The package consists of 
one class and it's associated methods:
- PrismSession
    - close
    - get_download_directory
    - set_download_directory
    - get_driver_wait
    - set_driver_wait
    - get_30_year_monthly_normals
    - get_30_year_daily_normals
    - get_annual_values
    - get_single_month_values
    - get_monthly_values
    - get_daily_values

Each weather getter method has two to three required arguments which are common to all of them. They are:
- **is_bulk_request**:
    - Set to True if you are providing a .csv for bulk location request. False otherise.
        - If set to True, you must provide a string csv_path.
        - If set to False, you must provide int/float latitude and longitude.
- **csv_path**:
    - A string path pointing to the .csv you want to use for a bulk request.
    - Your .csv input should have three columns:
        - Column 1: 
            - latitude: int/float
        - Column 2: 
            - longitude: int/float
        - Column 3: 
            - name: string fewer than 13 characters in length
- **latitude**:
    - An integer or floating point latitude coordinate.
- **longitude**:
    - An integer of floating point longitude coordinate.

There's also one optional arg common to all getter methods that I'll call out here:
- **download_dir**:
    - The directory where prism-pull will download the results of your PRISM queries.
    - **Default:** your current working directory
### PrismSession
Generate a new PrismSession:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()
```
Your PrismSession object can be initialized with two optional arguments:
- **driver_wait**:
    - The time (in seconds) prism-pull web driver will wait before moving onto the next step. Consider increasing if you have poor download speeds.
    - **Default:** 5 seconds

Here's an example of setting up a session with these arguments:
```
import prism_pull.prism_session as pp

session = pp.PrismSession(download_dir='absolute/path/to/download/to', driver_wait=10)
```
### close
Causes your session's WebDriver to quit. Run this command at the end of your session to clean up any associated WebDriver resources. Here's an example usage:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

<run your prism session commands>

session.close()
```
### get_download_directory
Returns the absolute path of your session's currently set download directory. Use as follows:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_download_directory()
```
### set_download_directory
Updates the directory where your PrismSession object will download data to. Here's an example:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.set_download_directory(<absolute or relative path to your target download dir>)
```
### get_driver_wait
Returns the driver wait time for your current PrismSession. Use similar to get_download_directory():
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_driver_wait()
```
### set_driver_wait
Updates the driver wait time for your current PrismSession. Consider increasing this if you're downloads aren't showing up, are getting cut off mid download, or if you know you have a bad internet connection. Consider that the largest possible file size from PRISM is 12.7MB. Conversely, if your internet is blazing fast, turn down the wait time. Here's how to use this method:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.set_driver_wait(10)
```
### get_30_year_monthly_normals
Returns the average monthly conditions over the previous three decades for the provided **latitude** and **longitude** or **csv_path**. Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_30_year_monthly_normals(
    is_bulk_request=False,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,
    cloud_transmittance=False,
    solar_rad_horiz_sfc=False,
    solar_rad_sloped_sfc=False,
    solar_rad_clear_sky=False
)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_30_year_monthly_normals(
    is_bulk_request=True,
    csv_path="tests/resources/small_coordinates.csv",
    max_temp=True,
    solar_rad_horiz_sfc=True,
    solar_rad_sloped_sfc=True
)
```
### get_30_year_daily_normals
Returns the average daily conditions over the previous three decades for the provided **latitude** and **longitude** or **csv_path**. Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_30_year_daily_normals(
    is_bulk_request=False,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,
)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_30_year_daily_normals(
    is_bulk_request=True,
    csv_path="tests/resources/small_coordinates.csv",
    max_temp=True,
    mean_temp=False
)
```
### get_annual_values
Returns average or total data for selected measurements for each year from **start_year** to **end_year**, for the provided **latitude** and **longitude** or **csv_path**. Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_annual_values(
    is_bulk_request=False,
    start_year=2015,
    end_year=2023,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,
)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_annual_values(
    is_bulk_request=False,
    start_year=1960,
    end_year=1966,
    csv_path="tests/resources/small_coordinates.csv",
    precipitation=False,
    max_temp=True,
    min_vpd=True,
    max_vpd=True,
)
```
### get_single_month_values
Returns average or total data for selected measurements for each **month** each year from **start_year** to **end_year**, for the provided **latitude** and **longitude** or **csv_path**. **NOTE:** any data collected within the past six months is considered provisional and may be subject to revisions. 

Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_single_month_values(
    is_bulk_request=False,
    month=4,
    start_year=1980,
    end_year=1990,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,
)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_single_month_values(
        is_bulk_request=True,
        month=11,
        start_year=2021,
        end_year=2024,
        csv_path="tests/resources/small_coordinates.csv",
        min_vpd=True,
        max_vpd=True,
)
```
### get_monthly_values
Returns average or total data for selected measurements for every month from **start_month**, **start_year** to **end_month**, **end_year**, for the provided **latitude** and **longitude** or **csv_path**. **NOTE:** there are some requirements and considerations for daily weather data:
- Any data collected within the past six months is considered provisional and may be subject to revisions.
- Your start and end dates must be within 15 years of each other.

Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_monthly_values(
    is_bulk_request=False,
    start_month=2,
    start_year=2011,
    end_month=9,
    end_year=2024,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,

)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_monthly_values(
    is_bulk_request=True,
    start_month=2,
    start_year=2011,
    end_month=9,
    end_year=2024,
    csv_path="tests/resources/small_coordinates.csv",
    precipitation=False,
    mean_dewpoint_temp=True,
)
```
### get_daily_values
Returns average or total data for selected measurements for each day from start_date, **start_month**, **start_year** to **end_date**, **end_month**, **end_year**, for the provided **latitude** and **longitude** or **csv_path**. **NOTE:** there are some requirements and considerations for daily weather data:
- Any data collected within the past six months is considered provisional and may be subject to revisions.
- Your start and end dates must be within one year of each other.

Here's an example usage showing a non-bulk request, and all the available weather inputs (precipitation, min_temp, etc.) set to their defaults:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_daily_values(
    is_bulk_request=False,
    start_date=16,
    start_month=11,
    start_year=1995,
    end_date=16,
    end_month=11,
    end_year=2009,
    latitude=40.9473,
    longitude=-112.2170,
    download_dir=CWD,
    precipitation=True,
    min_temp=False,
    mean_temp=True,
    max_temp=False,
    min_vpd=False,
    max_vpd=False,
    mean_dewpoint_temp=False,
)
```
Here's an example using a .csv for a bulk request, and setting a few non-default weather inputs:
```
import prism_pull.prism_session as pp

session = pp.PrismSession()

session.get_daily_values(
    is_bulk_request=True,
    start_date=16,
    start_month=11,
    start_year=1995,
    end_date=16,
    end_month=11,
    end_year=2009,
    csv_path="tests/resources/small_coordinates.csv",
    min_temp=True,
    min_vpd=True,
)
```
## Testing
This repo uses pytest for testing. In order to run locally, execute the following from the terminal:
```
pytest tests
```
## Contributing
If you work on this repo as a collaborator, shoot me an email at jtbaird95@gmail.com or create an issue and we'll get in touch.