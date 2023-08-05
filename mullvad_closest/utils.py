import requests
from dataclasses import dataclass
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from ping3 import ping
from geopy.distance import distance

class UnknownLocationType(Exception):
    pass

@dataclass
class Location:
    ip_address: str
    country: str
    city: str
    hostname: Optional[str] = None
    public_key: Optional[str] = None
    multihop_port: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    type: Optional[str] = None
    latency: Optional[float] = None
    distance_from_my_location: Optional[float] = None

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude

def get_my_location() -> Location:
    resp = requests.get("https://am.i.mullvad.net/json")
    resp.raise_for_status()
    data = resp.json()

    return Location(
        ip_address=data["ip"], country=data["country"], city=None, latitude=data["latitude"], longitude=data["longitude"]
    )

def fetch_and_parse_relays(only_location_type: Optional[str] = None) -> List[Location]:
    response = requests.get("https://api.mullvad.net/app/v1/relays")
    response.raise_for_status()

    data = response.json()
    locations = []
    for location_key, location_value in data["locations"].items():
        for relay in data["openvpn"]["relays"]:
            if relay["location"] == location_key:
                location = Location(
                    country=location_value["country"],
                    city=location_value["city"],
                    type="openvpn",
                    hostname=relay["hostname"],
                    ip_address=relay["ipv4_addr_in"],
                    public_key=relay.get("public_key", None),
                    multihop_port=relay.get("multihop_port", None),
                    latitude=location_value["latitude"],
                    longitude=location_value["longitude"],
                )
                locations.append(location)

    return locations

def get_closest_locations(
    locations: list[Location], max_distance: float = 500, location_type: Optional[str] = None
) -> list[Location]:
    my_location = get_my_location()

    locations_with_distance = []
    for location in locations:
        if location_type is not None and location.type != location_type:
            continue

        d = distance(my_location.coordinates, location.coordinates).km
        if d > max_distance:
            continue

        location.distance_from_my_location = d
        locations_with_distance.append(location)

    return sorted(
        locations_with_distance, key=lambda loc: (loc.distance_from_my_location is None, loc.distance_from_my_location)
    )

def ping_locations(locations: list[Location]) -> list[Location]:
    locations_with_latency = []

    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_location = {
            executor.submit(ping, location.ip_address, timeout=1, unit="ms"): location for location in locations
        }
        for future in as_completed(future_to_location):
            location = future_to_location[future]
            try:
                latency = future.result()
            except Exception as e:
                print(f"{location} raised an exception: {e}")
            else:
                location.latency = latency
                locations_with_latency.append(location)

    return sorted(locations_with_latency, key=lambda loc: (loc.latency is None, loc.latency))
