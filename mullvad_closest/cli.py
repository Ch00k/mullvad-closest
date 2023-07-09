from typing import Optional, Union

import click
from tabulate import tabulate

from . import utils

CONTEXT_SETTINGS = {"max_content_width": 120}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-s", "--server-type", type=click.Choice(["openvpn", "wireguard"]), help="Only show servers of a particular type"
)
@click.option(
    "-m", "--max-distance", default=500, show_default=True, help="Only show servers within this distance from myself"
)
def find(max_distance: float, server_type: Optional[str]) -> None:
    relays_file = utils.get_relays_file_path()
    locations = utils.parse_relays_file(relays_file, only_location_type=server_type)
    locations = utils.get_closest_locations(locations, max_distance=max_distance)
    locations = utils.ping_locations(locations)

    table_header = ["Country", "City", "Type", "IP", "Hostname", "Distance", "Latency"]
    table_data = [
        [
            loc.country,
            loc.city,
            loc.type,
            loc.ip_address,
            loc.hostname,
            loc.distance_from_my_location,
            parse_latency(loc.latency),
        ]
        for loc in locations
    ]
    click.echo(tabulate(table_data, headers=table_header))


def parse_latency(latency: Optional[Union[float, bool]]) -> str:
    if latency is None:
        return "timeout"
    elif latency is False:
        return "unresolvable"
    else:
        return str(latency)
