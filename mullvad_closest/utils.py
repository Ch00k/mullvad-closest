import json
import math
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import requests
from geopy.distance import distance
from ping3 import ping

RELAYS_FILE = "relays.json"


class UnknownLocationType(Exception):
    pass


@dataclass
class Location:
    ip_address: str
    country: str
    latitude: float
    longitude: float
    hostname: Optional[str] = None
    type: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None
    is_mullvad_owned: Optional[str] = None
    provider: Optional[str] = None
    latency: Optional[float | bool] = None
    distance_from_my_location: Optional[float] = None

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


def get_relays_file_path() -> Path:
    system = platform.system()

    if system == "Linux":
        path = Path("/var/cache/mullvad-vpn")
    elif system == "Darwin":
        path = Path("/Library/Caches/mullvad-vpn")
    elif system == "Windows":
        path = Path("C:/ProgramData/Mullvad VPN/cache")
    else:
        raise RuntimeError(f"Unsupported system: {system}")

    return path / "relays.json"


def get_my_location() -> Location:
    resp = requests.get("https://am.i.mullvad.net/json")
    resp.raise_for_status()
    data = resp.json()

    return Location(
        ip_address=data["ip"],
        country=data["country"],
        longitude=data["longitude"],
        latitude=data["latitude"],
    )


def parse_relays_file(relays_file: Path, only_location_type: Optional[str] = None) -> list[Location]:
    if not relays_file.exists():
        raise RuntimeError(f"{relays_file} does not exist")

    with open(relays_file, "r") as f:
        data = json.load(f)

    locations = []

    for country in data["countries"]:
        for city in country["cities"]:
            for relay in city["relays"]:
                # It's either of the following three:
                #
                # "endpoint_data": "openvpn"
                # "endpoint_data": "bridge"
                # "endpoint_data": {
                #   "wireguard": {
                #     "public_key": "foobarbaz"
                #   }
                # }
                try:
                    location_type = parse_location_type(relay["endpoint_data"])
                except UnknownLocationType as e:
                    print(e)
                    location_type = None

                if location_type == "bridge":
                    continue

                if only_location_type is not None and location_type != only_location_type:
                    continue

                locations.append(
                    Location(
                        ip_address=relay["ipv4_addr_in"],
                        country=country["name"],
                        latitude=city["latitude"],
                        longitude=city["longitude"],
                        hostname=relay["hostname"],
                        type=location_type,
                        city=city["name"],
                        is_active=relay["active"],
                        is_mullvad_owned=relay["owned"],
                        provider=relay["provider"],
                    )
                )

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
        locations_with_distance,
        key=lambda loc: (loc.distance_from_my_location is None, loc.distance_from_my_location),
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

    def latency_sort_key(loc: Location) -> float:
        if loc.latency in (None, False):
            return math.inf
        return loc.latency

    return sorted(locations_with_latency, key=latency_sort_key)


def parse_location_type(location_type: Union[str, dict]) -> str:
    if location_type in ("openvpn", "bridge"):
        return location_type
    if isinstance(location_type, dict):
        if "wireguard" in location_type:
            return "wireguard"

    raise UnknownLocationType(f"Location type {location_type} is not supported")
