import requests
import csv
import time
import argparse
import sys


def check_api_key(api_key):
    """Check if API key is provided."""
    if not api_key:
        print("ERROR: No Google API key provided.")
        print("This script requires a Google Maps API key.")
        print("Get a key from Google Cloud Console and run with:")
        print("  python script.py input.csv --api-key YOUR_KEY")
        sys.exit(1)


def get_address(place_name, country, api_key):
    """Get address using Google Geocoding API."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        'address': f"{place_name}, {country}",
        'key': api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['status'] == 'OK' and data['results']:
        return data['results'][0]['formatted_address'], data['results'][0].get('geometry', {}).get('location', {})
    else:
        return f"Address not found for {place_name}, {country}", None


def read_input_file(file_path):
    """Read input file containing place names and countries."""
    places = []
    
    # Check file extension to determine format
    if file_path.lower().endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Skip header row
            
            # Find place and country columns
            place_idx = 0
            country_idx = 1
            
            if header:
                for i, col in enumerate(header):
                    if col.lower() in ('place', 'place name', 'location', 'store'):
                        place_idx = i
                    elif col.lower() in ('country', 'nation'):
                        country_idx = i
            
            for row in reader:
                if len(row) > max(place_idx, country_idx):
                    places.append((row[place_idx], row[country_idx]))
    
    elif file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    places.append((parts[0].strip(), parts[1].strip()))
                elif len(parts) == 1 and parts[0].strip():
                    # If only place is provided, use default country
                    places.append((parts[0].strip(), ""))
    
    return places


def write_output_file(file_path, results):
    """Write results to a CSV file."""
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Place', 'Country', 'Address', 'Latitude', 'Longitude'])
        
        for place, country, address, coords in results:
            lat = coords['lat'] if coords else ''
            lng = coords['lng'] if coords else ''
            writer.writerow([place, country, address, lat, lng])


def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Find addresses for a list of places and countries using Google Maps API.')
    parser.add_argument('input_file', help='Path to input file (CSV or TXT)')
    parser.add_argument('--output', '-o', help='Path to output file (default: addresses_output.csv)', 
                      default='addresses_output.csv')
    parser.add_argument('--api-key', '-k', required=True, help='Google Maps API key (required)')
    parser.add_argument('--default-country', '-c', help='Default country if not specified (optional)')
    
    args = parser.parse_args()
    
    # Check API key
    check_api_key(args.api_key)
    
    # Read input file
    places = read_input_file(args.input_file)
    
    if not places:
        print(f"No valid places found in {args.input_file}")
        return
    
    # Process each place
    results = []
    for i, (place, country) in enumerate(places):
        # Use default country if provided and country is empty
        if not country and args.default_country:
            country = args.default_country
            
        print(f"Processing {i+1}/{len(places)}: {place}, {country}")
        
        address, coords = get_address(place, country, args.api_key)
        results.append((place, country, address, coords))
        
        # Respect Google API rate limits - not strictly necessary but good practice
        time.sleep(0.2)
    
    # Write results to output file
    write_output_file(args.output, results)
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()