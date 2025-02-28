import requests
import csv
import time
import sys
import json
from urllib.parse import quote

# ========================================================
# ADDRESS FINDER - FREE VERSION (NO GEOPY, NO GOOGLE API)
# ========================================================

def get_address_from_nominatim(place_name, country):
    """Get address using Nominatim (OpenStreetMap) API directly via HTTP."""
    # Encode the query parameters properly
    query = quote(f"{place_name}, {country}")
    
    # Nominatim API endpoint
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=1"
    
    # Add a user agent header as required by Nominatim's usage policy
    headers = {
        "User-Agent": "AddressFinder/1.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        # Wait to respect Nominatim's usage policy (max 1 request per second)
        time.sleep(1)
        
        # Make the request
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Process the response
        if data and len(data) > 0:
            result = data[0]
            address = result.get("display_name", "")
            lat = result.get("lat")
            lon = result.get("lon")
            
            coords = {"lat": lat, "lng": lon} if lat and lon else None
            return address, coords
        else:
            return f"Address not found for {place_name}, {country}", None
            
    except Exception as e:
        return f"Error finding address for {place_name}, {country}: {str(e)}", None


def process_csv_file(input_file, output_file, default_country=None):
    """Process a CSV file containing place names and countries."""
    try:
        # Open the input file
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Skip header
            
            # If there's no header, we'll need to reopen the file
            if not header:
                infile.seek(0)
                reader = csv.reader(infile)
            
            # Determine column indices
            place_idx, country_idx = 0, 1
            if header:
                for i, col in enumerate(header):
                    col_lower = col.lower()
                    if col_lower in ('place', 'place name', 'location', 'store'):
                        place_idx = i
                    elif col_lower in ('country', 'nation'):
                        country_idx = i
            
            # Read all places and countries
            places = []
            for row in reader:
                if len(row) > max(place_idx, country_idx):
                    place = row[place_idx].strip()
                    country = row[country_idx].strip() if len(row) > country_idx else ''
                    
                    # Use default country if provided and country is empty
                    if not country and default_country:
                        country = default_country
                    
                    places.append((place, country))
        
        # If no places found
        if not places:
            print(f"No valid places found in {input_file}")
            return False
        
        # Process each place and collect results
        results = []
        for i, (place, country) in enumerate(places):
            print(f"Processing {i+1}/{len(places)}: {place}, {country}")
            
            address, coords = get_address_from_nominatim(place, country)
            results.append((place, country, address, coords))
        
        # Write results to output file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Place', 'Country', 'Address', 'Latitude', 'Longitude'])
            
            for place, country, address, coords in results:
                lat = coords['lat'] if coords else ''
                lng = coords['lng'] if coords else ''
                writer.writerow([place, country, address, lat, lng])
        
        print(f"Results saved to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main function to run the script."""
    # Check if required packages are installed
    try:
        import requests
    except ImportError:
        print("Error: The 'requests' package is not installed.")
        print("Please install it using: pip install requests")
        return
    
    # Simple command line argument parsing
    args = sys.argv[1:]
    
    if not args or '--help' in args or '-h' in args:
        print("Usage: python script.py INPUT_FILE [--output OUTPUT_FILE] [--default-country COUNTRY]")
        print("\nOptions:")
        print("  INPUT_FILE                Path to input CSV file with places and countries")
        print("  --output, -o FILE         Output file path (default: addresses_output.csv)")
        print("  --default-country, -c     Default country if not specified in input")
        return
    
    # Parse arguments
    input_file = args[0]
    output_file = "addresses_output.csv"
    default_country = None
    
    i = 1
    while i < len(args):
        if args[i] in ('--output', '-o') and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] in ('--default-country', '-c') and i + 1 < len(args):
            default_country = args[i + 1]
            i += 2
        else:
            i += 1
    
    # Process the file
    print("Using OpenStreetMap Nominatim (free geocoding service)")
    print("Note: This service has a limit of 1 request per second")
    process_csv_file(input_file, output_file, default_country)


if __name__ == "__main__":
    main()