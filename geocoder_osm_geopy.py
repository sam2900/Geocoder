import csv
import time
import sys
import os

# First, try to install geopy if it's not already installed
try:
    import geopy
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_INSTALLED = True
except ImportError:
    GEOPY_INSTALLED = False
    print("Warning: geopy is not installed. Attempting to install it now...")
    
    # Try to install geopy using pip
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "geopy"])
        print("geopy installed successfully!")
        import geopy
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        GEOPY_INSTALLED = True
    except Exception as e:
        print(f"Failed to install geopy: {e}")
        print("Please install geopy manually with: pip install geopy")
        print("Continuing with direct HTTP requests instead...")


def get_address_using_geopy(place_name, country):
    """Get address using geopy's Nominatim geocoder."""
    try:
        # Initialize the geocoder with a custom user agent
        geolocator = Nominatim(user_agent="address_finder_app")
        
        # Geocode the location
        query = f"{place_name}, {country}" if country else place_name
        location = geolocator.geocode(query)
        
        if location:
            # Format the coordinates
            coords = {"lat": location.latitude, "lng": location.longitude}
            return location.address, coords
        else:
            return f"Address not found for {place_name}, {country}", None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return f"Geocoding service error for {place_name}, {country}: {str(e)}", None
    except Exception as e:
        return f"Error finding address for {place_name}, {country}: {str(e)}", None


def get_address_via_http(place_name, country):
    """Get address using Nominatim (OpenStreetMap) API directly via HTTP."""
    import requests
    from urllib.parse import quote
    
    # Encode the query parameters properly
    query = quote(f"{place_name}, {country}" if country else place_name)
    
    # Nominatim API endpoint
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=1"
    
    # Add a user agent header as required by Nominatim's usage policy
    headers = {
        "User-Agent": "AddressFinder/1.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
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


def get_address(place_name, country):
    """Get address using the best available method."""
    # Wait to respect Nominatim's usage policy (max 1 request per second)
    time.sleep(1)
    
    # Use geopy if available, otherwise fallback to HTTP requests
    if GEOPY_INSTALLED:
        return get_address_using_geopy(place_name, country)
    else:
        try:
            import requests
            return get_address_via_http(place_name, country)
        except ImportError:
            print("Error: The 'requests' package is not installed.")
            print("Please install it using: pip install requests")
            sys.exit(1)


def read_input_file(file_path):
    """Read input file containing place names and countries."""
    places = []
    
    try:
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
                        if col and col.lower() in ('place', 'place name', 'location', 'store'):
                            place_idx = i
                        elif col and col.lower() in ('country', 'nation'):
                            country_idx = i
                
                for row in reader:
                    if len(row) > place_idx:
                        place = row[place_idx].strip()
                        country = row[country_idx].strip() if len(row) > country_idx else ''
                        places.append((place, country))
        
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        places.append((parts[0].strip(), parts[1].strip()))
                    elif len(parts) == 1 and parts[0].strip():
                        # If only place is provided, use empty country string
                        places.append((parts[0].strip(), ""))
                        
        else:
            print(f"Unsupported file format: {file_path}")
            print("Please use a CSV or TXT file.")
            return []
    
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return []
        
    return places


def write_output_file(file_path, results):
    """Write results to a CSV file."""
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Place', 'Country', 'Address', 'Latitude', 'Longitude'])
            
            for place, country, address, coords in results:
                lat = coords['lat'] if coords else ''
                lng = coords['lng'] if coords else ''
                writer.writerow([place, country, address, lat, lng])
        
        return True
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        return False


def main():
    """Main function to run the script."""
    # Simple command line argument parsing
    args = sys.argv[1:]
    
    if not args or '--help' in args or '-h' in args:
        print("Usage: python script.py INPUT_FILE [--output OUTPUT_FILE] [--default-country COUNTRY]")
        print("\nOptions:")
        print("  INPUT_FILE                Path to input CSV or TXT file with places and countries")
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
    
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    # Report which method is being used
    if GEOPY_INSTALLED:
        print("Using geopy with OpenStreetMap Nominatim service")
    else:
        print("Using direct HTTP requests to OpenStreetMap Nominatim service")
    print("Note: This service has a limit of 1 request per second")
    
    # Read input file
    places = read_input_file(input_file)
    
    if not places:
        print(f"No valid places found in {input_file}")
        return
    
    # Process each place
    results = []
    print(f"Processing {len(places)} locations...")
    
    for i, (place, country) in enumerate(places):
        # Use default country if provided and country is empty
        if not country and default_country:
            country = default_country
            
        print(f"Processing {i+1}/{len(places)}: {place}, {country}")
        
        address, coords = get_address(place, country)
        results.append((place, country, address, coords))
    
    # Write results to output file
    if write_output_file(output_file, results):
        print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()