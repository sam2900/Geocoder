# Geocoder Tool

A collection of Python scripts for geocoding addresses from place names using multiple data sources.

![Geocoder Tool Banner](https://github.com/sam2900/Geocoder/blob/main/banner.png)

## Overview

This tool allows you to find addresses and coordinates for a list of place names using different geocoding services:

1. **Google Maps Geocoding API** - Requires a Google API key (paid service)
2. **OpenStreetMap via geopy** - Free service using the geopy library
3. **OpenStreetMap via HTTP** - Free service using direct HTTP requests (no dependencies except requests)

## Requirements

- Python 3.6 or higher
- Required packages (automatically installed for some methods):
  - `requests` - For HTTP requests to APIs
  - `geopy` - For the OpenStreetMap via geopy method (will auto-install if needed)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/sam2900/Geocoder.git
   cd Geocoder
   ```

2. Install the required packages:
   ```
   pip install requests
   ```

3. Optional: Install geopy (will be auto-installed by the script if needed):
   ```
   pip install geopy
   ```

## Input File Format

The tool accepts CSV or TXT files as input with the following format:

### CSV Format
The CSV file should contain at least two columns:
- A column for place names (default: first column)
- A column for country names (default: second column)

Example CSV:
```
Place,Country
New York,USA
Paris,France
Tokyo,Japan
```

The script will try to auto-detect columns with these headers:
- Place column: "place", "place name", "location", or "store"
- Country column: "country" or "nation"

### TXT Format
For TXT files, each line should contain a place name and country, separated by a comma:
```
New York,USA
Paris,France
Tokyo,Japan
```

## Usage

### Using the Interactive Tool

Run the interactive tool to select your preferred geocoding method:

```
python tool.py
```

Follow the on-screen instructions to select a geocoding method and provide the required parameters.

### Direct Script Usage

You can also run any of the scripts directly:

#### 1. Google Maps Geocoding API (requires API key)

```
python geocoder_google_api.py input.csv --api-key YOUR_GOOGLE_API_KEY [--output output.csv] [--default-country USA]
```

#### 2. OpenStreetMap via geopy (free)

```
python geocoder_osm_geopy.py input.csv [--output output.csv] [--default-country USA]
```

#### 3. OpenStreetMap via HTTP (free, minimal dependencies)

```
python geocoder_osm_http.py input.csv [--output output.csv] [--default-country USA]
```

## Output

The output is a CSV file with the following columns:
- Place: The original place name
- Country: The original country name
- Address: The formatted address found by the geocoding service
- Latitude: The latitude coordinate
- Longitude: The longitude coordinate

Example output:
```
Place,Country,Address,Latitude,Longitude
New York,USA,"New York, NY, USA",40.7127753,-74.0059728
Paris,France,"Paris, France",48.856614,2.3522219
Tokyo,Japan,"Tokyo, Japan",35.6761919,139.6503106
```

## Command Line Arguments

All scripts support the following arguments:

- `input_file`: Path to the input CSV or TXT file (required)
- `--output` or `-o`: Path to the output CSV file (default: addresses_output.csv)
- `--default-country` or `-c`: Default country to use if not specified in the input file

The Google API script additionally requires:
- `--api-key` or `-k`: Your Google Maps API key

## Service Rate Limits

- **Google Maps API**: Depends on your billing plan
- **OpenStreetMap (Nominatim)**: Maximum 1 request per second (enforced by the scripts)

## Notes

- The OpenStreetMap scripts include a 1-second delay between requests to comply with Nominatim's usage policy.
- When using the Google API, ensure your API key has the Geocoding API enabled.
- For large datasets, consider using the Google API as it has higher rate limits for paid users.

## Troubleshooting

- If you get an error about missing packages, run `pip install requests` or `pip install geopy`.
- If the OpenStreetMap services don't return results, try specifying the country to narrow down the search.
- For Google API errors, verify that your API key is correct and has the Geocoding API enabled.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) for providing free geocoding services
- [Google Maps Platform](https://cloud.google.com/maps-platform/) for their geocoding API
- [geopy](https://github.com/geopy/geopy) for their geocoding library
