import googlemaps
import os
from datetime import datetime

TRANSPORT_MODES = ["driving", "walking", "bicycling", "transit"]
gmaps = googlemaps.Client(key=os.getenv("GMAPS_API_KEY", ""))

def retrieve_routes(start, end, mode="walking"):
    return gmaps.directions(start, end, mode=mode, departure_time=datetime.now())