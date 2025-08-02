import logging
import re
from typing import List
import requests
from bs4 import BeautifulSoup

def get_19hz_events(region: str = "la") -> List[dict]:
    """
    Scrapes events from 19hz.info, which focuses on electronic music events
    in various US regions.
    
    Args:
        region: The region to scrape (sf, la, seattle, atlanta, miami, dc, etc.)
    
    Returns:
        A list of event data dictionaries scraped from 19hz.info
    """
    
    # 19hz.info has different pages for different regions
    region_urls = {
        "sf": "https://19hz.info/eventlisting_BayArea.php",  # Bay Area
        "la": "https://19hz.info/eventlisting_LosAngeles.php",
        "seattle": "https://19hz.info/eventlisting_Seattle.php", 
        "atlanta": "https://19hz.info/eventlisting_Atlanta.php",
        "miami": "https://19hz.info/eventlisting_Miami.php",
        "dc": "https://19hz.info/eventlisting_DC.php",
        "chicago": "https://19hz.info/eventlisting_Chicago.php",
        "detroit": "https://19hz.info/eventlisting_Detroit.php",
        "denver": "https://19hz.info/eventlisting_Denver.php",
        "vegas": "https://19hz.info/eventlisting_LasVegas.php",
        "portland": "https://19hz.info/eventlisting_Portland.php"
    }
    
    url = region_urls.get(region.lower(), region_urls["sf"])
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events = []
        
        # Find the table rows - 19hz uses a simple table structure
        table_rows = soup.find_all('tr')
        
        for row in table_rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 2:  # Skip header rows or incomplete rows
                    continue
                
                # Extract data from table cells
                # Based on the curl output structure: Date/Time | Event Title @ Venue | Tags | Price | Organizers | Links
                date_cell = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                event_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                tags_cell = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                price_cell = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                organizer_cell = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                
                # Skip if no meaningful event data
                if not event_cell or len(event_cell) < 5:
                    continue
                
                # The event_cell contains everything concatenated: 
                # "Event Name @ Venue (City)tagspricedateorganizer"
                # We need to parse this properly
                
                # First, look for the @ symbol to split event name and venue+rest
                if '@ ' in event_cell:
                    event_parts = event_cell.split('@ ', 1)
                    event_name = event_parts[0].strip()
                    rest_of_data = event_parts[1].strip()
                    
                    # Now we need to extract venue, city, and date from rest_of_data
                    # Look for date pattern at the end (YYYY/MM/DD format)
                    date_match = re.search(r'(\d{4}/\d{2}/\d{2})$', rest_of_data)
                    if date_match:
                        date_str = date_match.group(1)
                        # Remove the date from the end
                        venue_and_more = rest_of_data[:date_match.start()].strip()
                    else:
                        date_str = date_cell  # fallback to original date cell
                        venue_and_more = rest_of_data
                    
                    # Extract venue and city from the beginning of venue_and_more
                    # Format is usually "Venue Name (City)" followed by other stuff
                    venue_match = re.match(r'^([^(]+)\s*\(([^)]+)\)', venue_and_more)
                    if venue_match:
                        venue = venue_match.group(1).strip()
                        city = venue_match.group(2).strip()
                    else:
                        # Fallback: try to find any venue name before other data
                        venue_parts = venue_and_more.split()
                        if venue_parts:
                            venue = venue_parts[0]
                            city = "UNKNOWN" 
                        else:
                            venue = "Unknown Venue"
                            city = "UNKNOWN"
                else:
                    # If no @ symbol, treat the whole thing as event name
                    event_name = event_cell
                    venue = "Unknown Venue"
                    city = "UNKNOWN"
                    date_str = date_cell
                
                # Extract artists from event name
                artists = []
                artist_text = event_name
                
                # Remove common prefixes and clean up
                artist_text = re.sub(r'^(SAT|SUN|MON|TUE|WED|THU|FRI)[\s:]+', '', artist_text, flags=re.IGNORECASE)
                
                # Look for event title patterns like "Event Name: Artist1, Artist2"
                if ':' in artist_text:
                    parts = artist_text.split(':', 1)
                    if len(parts) > 1:
                        # Use the part after the colon for artists
                        artist_names = re.split(r'[,&+]|(?:\s+(?:w/|with|and|b2b|B2B)\s+)', parts[1].strip())
                        artists = [name.strip() for name in artist_names if name.strip()][:5]
                    else:
                        artists = [parts[0].strip()]
                elif any(sep in artist_text for sep in [',', ' & ', ' and ', ' + ', ' w/ ', ' with ', ' b2b ', ' B2B ']):
                    # Split by common separators for artists
                    artist_names = re.split(r'[,&+]|(?:\s+(?:w/|with|and|b2b|B2B)\s+)', artist_text)
                    artists = [name.strip() for name in artist_names if name.strip()][:5]
                else:
                    # Use the whole event name as a single artist
                    artists = [artist_text.strip()] if artist_text.strip() else []
                
                # Clean up artist names (remove extra whitespace, empty strings)
                artists = [artist for artist in artists if artist and len(artist.strip()) > 0][:5]
                
                events.append({
                    'id': f"19hz-{len(events)}",
                    'title': event_name,
                    'date': date_str,  # Use the extracted date
                    'venue': venue,
                    'location': city,
                    'artists': artists,
                    'tags': tags_cell,
                    'price': price_cell,
                    'organizer': organizer_cell
                })
                    
            except Exception as e:
                logging.warning(f"Could not parse event row: {e}")
                continue
        
        logging.info(f"Found {len(events)} events from 19hz.info")
        return events
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from 19hz.info: {e}")
        return [] 