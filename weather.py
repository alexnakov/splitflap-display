import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional

import requests

# Ordered list of locations to cycle through on the board
WEATHER_LOCATIONS: List[Dict[str, str]] = [
    {
        "key": "LONDON",
        "display": "LONDON, UK",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London",
    },
    {
        "key": "CHICAGO",
        "display": "CHICAGO, USA",
        "latitude": 41.8832,
        "longitude": -87.6324,
        "timezone": "America/chicago",
    },
    {
        "key": "TOKYO",
        "display": "TOKYO, JAPAN",
        "latitude": 35.6764,
        "longitude": 139.6500,
        "timezone": "Asia/Tokyo",
    },
    {
        "key": "BERLIN",
        "display": "BERLIN, GERMANY",
        "latitude": 52.5200,
        "longitude": 13.4050,
        "timezone": "Europe/Berlin",
    },{
        "key": "SYDNEY",
        "display": "SYDNEY, AUSTRALIA",
        "latitude": -33.8727,
        "longitude": 151.2057,
        "timezone": "Australia/Sydney",
    }
]

_LOCATION_MAP: Dict[str, Dict[str, str]] = {
    loc["key"]: loc for loc in WEATHER_LOCATIONS
}

MOCK_WEATHER_BOARDS: Dict[str, List[str]] = {
    "LONDON": [
        "LONDON, UK",
        "",
        "LOCAL TIME 09:45 AM",
        "TEMP       12°C",
        r"RAIN       15%",
        "BRISK SPRING BREEZE",
    ],
    "NEWARK_ON_TRENT": [
        "NEWARK-ON-TRENT, UK",
        "",
        "LOCAL TIME 09:45 AM",
        "TEMP       12°C",
        r"RAIN       35%",
        "MIST LIFTING STEADY",
    ],
    "PLOVDIV": [
        "PLOVDIV, BULGARIA",
        "",
        "LOCAL TIME 11:45 AM",
        "TEMP       12°C",
        r"RAIN       25%",
        "SUN WITH PASSING CLOUD",
    ],
}


def _fetch_location_weather(location_key: str) -> Dict[str, Optional[float]]:
    """
    Query Open-Meteo for the given location.
    Returns a dict with temp_c, rain_prob, desc.
    """
    config = _LOCATION_MAP.get(location_key.upper())
    if not config:
        raise ValueError(f"Unknown weather location '{location_key}'")

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={config['latitude']}&longitude={config['longitude']}"
        "&hourly=temperature_2m,precipitation_probability"
        "&current_weather=true"
        f"&timezone={config['timezone']}"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        temp = current.get("temperature")
        current_time = current.get("time")
        rain_prob = None

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        probs = hourly.get("precipitation_probability", [])
        if current_time and times and probs:
            try:
                idx = times.index(current_time)
                rain_prob = probs[idx]
            except ValueError:
                pass

        if rain_prob is None:
            desc = "HAVE A GREAT DAY!"
        elif rain_prob < 20:
            desc = "CLEAR SKIES EXPECTED"
        elif rain_prob < 50:
            desc = "PARTLY CLOUDY CONDITIONS"
        else:
            desc = "SHOWERS LIKELY PACK UMB"

        return {"temp_c": temp, "rain_prob": rain_prob, "desc": desc}
    except Exception as exc:
        print(f"Weather fetch failed for {location_key}: {exc}")
        return {"temp_c": None, "rain_prob": None, "desc": "NO DATA AVAILABLE"}


def _fit(text: str, width: int = 22) -> str:
    """Trim or pad text to fit the split-flap cell width."""
    text = text.strip().upper()
    if len(text) > width:
        return text[:width]
    return text.ljust(width)


def fetch_weather_update(location_key: str, use_mock: bool = False) -> List[str]:
    """
    Return 6 board lines (<=22 chars each) for the requested location.
    """
    if not _LOCATION_MAP:
        raise RuntimeError("No weather locations configured.")

    location = _LOCATION_MAP.get(location_key.upper())
    if not location:
        raise ValueError(f"Unknown weather location '{location_key}'")

    if use_mock:
        mock_board = MOCK_WEATHER_BOARDS.get(location_key.upper())
        if mock_board:
            return [_fit(line) for line in mock_board]

    readings = _fetch_location_weather(location_key)
    tz = ZoneInfo(location["timezone"])
    now = datetime.datetime.now(tz)


    time_line = now.strftime("%I:%M %p")
    if time_line.startswith("0"):
        time_line = " " + time_line[1:]
    temp_line = "--°C" if readings["temp_c"] is None else f"{int(round(readings['temp_c']))}°C"
    rain_line = "--%" if readings["rain_prob"] is None else f"{int(round(readings['rain_prob']))}%"
    desc_line = readings["desc"]

    return [
        _fit(location["display"]),
        _fit(""),
        _fit(f"LOCAL TIME {time_line}"),
        _fit(f"TEMP" + 5*" " + f"{temp_line.rjust(6)}"),
        _fit(f"RAIN" + 4*" " + f"{rain_line.rjust(6)}"),
        _fit(desc_line),
    ]
