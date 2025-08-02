import logging
from datetime import datetime, timezone
from typing import Optional
import re
from src.schema import MusicEvent
from src.config import DEFAULT_COUNTRY

def normalize_ra_event(event_data: dict) -> Optional[MusicEvent]:
    """
    Normalizes events from various sources into our MusicEvent schema.
    """
    try:
        # Handle date parsing
        date_str = event_data.get('date', '')
        if date_str:
            try:
                # Try parsing various date formats
                current_year = datetime.now().year
                
                if 'T' in date_str:
                    # ISO format
                    parsed_date = datetime.fromisoformat(date_str.replace('Z', ''))
                    iso_date = parsed_date.isoformat() + "Z"
                else:
                    # Try common formats with current year
                    
                    # Handle "Aug 15", "September 3" etc.
                    month_match = re.search(r'(\w+)\s+(\d{1,2})', date_str)
                    if month_match:
                        month_name, day = month_match.groups()
                        try:
                            parsed_date = datetime.strptime(f"{month_name} {day} {current_year}", '%B %d %Y')
                        except ValueError:
                            parsed_date = datetime.strptime(f"{month_name} {day} {current_year}", '%b %d %Y')
                        iso_date = parsed_date.isoformat() + "Z"
                    else:
                        # Try other formats
                        for fmt in ['%m/%d', '%m-%d', '%d/%m', '%d-%m']:
                            try:
                                parsed_date = datetime.strptime(f"{date_str}/{current_year}", f"{fmt}/%Y")
                                iso_date = parsed_date.isoformat() + "Z"
                                break
                            except ValueError:
                                continue
                        else:
                            # If no format works, use current time
                            iso_date = datetime.now(timezone.utc).isoformat()
            except Exception:
                iso_date = datetime.now(timezone.utc).isoformat()
        else:
            iso_date = datetime.now(timezone.utc).isoformat()

        # Parse location (city, country)
        location = event_data.get('location', '')
        city = location if location != 'Unknown City' else 'Los Angeles'  # Default for 19hz
        country_name = 'United States'  # 19hz is US-focused

        return {
            "id": event_data.get('id', f"event-{datetime.now().timestamp()}"),
            "name": event_data.get('title', 'Electronic Music Event'),
            "artists": event_data.get('artists', []),
            "venue": event_data.get('venue', 'Unknown Venue'),
            "city": city,
            "country": country_name,
            "date": iso_date,
        }
    except Exception as e:
        logging.warning(f"Could not normalize event due to error: {e}. Event data: {event_data}")
        return None 