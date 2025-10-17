import requests
import datetime

def fetch_london_weather():
    """
    Fetch current temperature and precipitation probability for London
    using the free Open-Meteo API (no API key required).
    Returns a dict with: temp_c, rain_prob, desc
    """
    lat, lon = 51.5074, -0.1278
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation_probability"
        "&current_weather=true"
        "&timezone=Europe/London"
    )
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        cw = data.get("current_weather", {})
        temp = cw.get("temperature")
        time_now = cw.get("time")
        rain_prob = None

        # Try to extract rain probability from hourly data
        hr = data.get("hourly", {})
        times = hr.get("time", [])
        probs = hr.get("precipitation_probability", [])
        if time_now and times and probs:
            try:
                idx = times.index(time_now)
                rain_prob = probs[idx]
            except ValueError:
                pass

        # Describe weather briefly
        if rain_prob is None:
            desc = "WEATHER UNKNOWN"
        elif rain_prob < 20:
            desc = "SKIES CLEAR AND BRIGHT"
        elif rain_prob < 50:
            desc = "PARTLY CLOUDY MORNING"
        else:
            desc = "SHOWERS EXPECTED LATER"

        return {"temp_c": temp, "rain_prob": rain_prob, "desc": desc}
    except Exception as e:
        print("Weather fetch failed:", e)
        return {"temp_c": None, "rain_prob": None, "desc": "NO DATA AVAILABLE"}

def fetch_weather_update():
    """
    Returns a list of 6 strings (each <=22 chars) for a Station-Board Classic layout.
    """
    w = fetch_london_weather()
    location = "LONDON"
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    timestr = now.strftime("%I:%M %p").lstrip("0")  # e.g. 7:45 AM

    temp = "--°C" if w["temp_c"] is None else f"{int(round(w['temp_c']))}°C"
    rain = "--%" if w["rain_prob"] is None else f"{int(round(w['rain_prob']))}%"
    desc = w["desc"][:22].upper()

    # Helper to fit strings cleanly to 22 chars
    def fit(s, width=22, align="left"):
        s = s.strip()
        if len(s) > width:
            s = s[:width]
        return s.ljust(width) if align == "left" else s.rjust(width)

    board = [
        fit(f"{location} MORNING REPORT"),
        fit(f"TIME          {timestr}"),
        fit(f"TEMP             {temp}"),
        fit(f"RAIN PROB.         {rain}"),
        fit(desc),
        fit("HAVE A GOOD DAY!"),
    ]
    return board
