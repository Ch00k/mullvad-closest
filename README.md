# mullvad-closest

*mullvad-closest* helps pick a server that would have the lowest latency at (and would usually be the closest to) your
current location.

Your current location is taken from the response of https://am.i.mullvad.net/json (the API that powers
https://mullvad.net/check).

List of Mullvad servers is provided by `relays.json`, a file that is bundled with Mullvad application. Depending on your
platform, it can be found in the following locations on the filesystem:

- Linux: `/var/cache/mullvad-vpn/relays.json`
- macOS: `/Library/Caches/mullvad-vpn/relays.json`
- Windows: `C:\ProgramData\Mullvad VPN\cache\relays.json`

The distance between your location and a Mullvad server is the [geodesic
distance](https://en.wikipedia.org/wiki/Geodesics_on_an_ellipsoid) in kilometers. By default only the servers within 500
km are shown.

The latency is the result of one ICMP request sent to the server's IP address.

## Installation

Install with [pipx](https://github.com/pypa/pipx):

```
$ pipx install mullvad-closest
```

## Usage
```
$ mullvad-closest --help
Usage: mullvad-closest [OPTIONS]

Options:
  -s, --server-type [openvpn|wireguard]
                                  Only show servers of a particular type
  -m, --max-distance INTEGER      Only show servers within this distance from myself  [default: 500]
  --help                          Show this message and exit.
```

Find all WireGuard servers within 300 kilometers:

```
$ mullvad-closest --max-distance 300 --server-type wireguard
Country      City        Type       IP              Hostname         Distance    Latency
-----------  ----------  ---------  --------------  -------------  ----------  ---------
Netherlands  Amsterdam   wireguard  193.32.249.70   nl-ams-wg-005     31.3219    18.8773
Netherlands  Amsterdam   wireguard  193.32.249.69   nl-ams-wg-004     31.3219    18.9524
Netherlands  Amsterdam   wireguard  193.32.249.66   nl-ams-wg-001     31.3219    20.0162
Netherlands  Amsterdam   wireguard  169.150.196.15  nl-ams-wg-202     31.3219    21.9269
Netherlands  Amsterdam   wireguard  185.65.134.83   nl-ams-wg-003     31.3219    22.2118
Netherlands  Amsterdam   wireguard  169.150.196.28  nl-ams-wg-203     31.3219    22.5372
Netherlands  Amsterdam   wireguard  169.150.196.2   nl-ams-wg-201     31.3219    22.8589
Netherlands  Amsterdam   wireguard  185.65.134.86   nl-ams-wg-006     31.3219    22.8741
Netherlands  Amsterdam   wireguard  185.65.134.82   nl-ams-wg-002     31.3219    22.9678
Germany      Dusseldorf  wireguard  185.254.75.5    de-dus-wg-003    150.785     24.272
Germany      Dusseldorf  wireguard  185.254.75.3    de-dus-wg-001    150.785     24.287
Luxembourg   Luxembourg  wireguard  92.223.89.181   lu-lux-wg-001    285.289     24.3261
Luxembourg   Luxembourg  wireguard  92.223.89.165   lu-lux-wg-002    285.289     24.3518
Germany      Dusseldorf  wireguard  185.254.75.4    de-dus-wg-002    150.785     25.2352
Belgium      Brussels    wireguard  91.90.123.2     be-bru-wg-101    149.609     25.6422
Netherlands  Amsterdam   wireguard  92.60.40.209    nl-ams-wg-102     31.3219    25.7621
Netherlands  Amsterdam   wireguard  92.60.40.239    nl-ams-wg-104     31.3219    26.2949
Netherlands  Amsterdam   wireguard  92.60.40.194    nl-ams-wg-101     31.3219    26.3009
Netherlands  Amsterdam   wireguard  92.60.40.224    nl-ams-wg-103     31.3219    26.3679
Belgium      Brussels    wireguard  194.110.115.34  be-bru-wg-102    149.609     28.5451
Belgium      Brussels    wireguard  194.110.115.2   be-bru-wg-103    149.609     28.6839

```
