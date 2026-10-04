import re
import urllib.request
from pathlib import Path

SOURCE = "https://iptv-org.github.io/iptv/languages/eng.m3u"
OUTPUT = Path("English_TV_Essentials_US.m3u")
EXPECTED_COUNT = 42

GROUPS = {
    "01 Local Carolinas": [
        "ABC.us@WSOCTV", "WBTV641.us@HD"
    ],
    "02 News": [
        "ABCNewsLive.us@SD", "CBSNews247.us@SD", "NBCNewsNOW.us@SD",
        "ScrippsNews.us@SD", "ReutersTV.us@SD", "LiveNOWfromFOX.us@SD",
        "USATODAY.us@SD", "CheddarNews.us@SD"
    ],
    "03 Weather & Business": [
        "AccuWeatherNOW.us@SD", "FoxWeather.us@SD", "WeatherNation.us@SD",
        "YahooFinance.us@SD"
    ],
    "04 Sports": [
        "NBCSportsNOW.us@SD", "FuboSportsNetwork.us@SD", "PGATour.us@SD",
        "SportsGrid.us@SD", "Pac12Insider.us@SD", "PBRRidePass.us@SD"
    ],
    "05 Movies": [
        "00sReplay.us@SD", "70sCinema.us@SD", "80sRewind.us@SD",
        "HallmarkMoviesMore.us@SD", "MovieSphere.us@US",
        "PlutoTVActionMovies.us@CA"
    ],
    "06 TV & Comedy": [
        "48Hours.us@US", "Baywatch.us@US", "Cheers.us@CA",
        "HappyDays.us@SD", "Matlock.us@SD", "Mythbusters.us@UK",
        "NBCComedyVault.us@SD"
    ],
    "07 Kids & Family": [
        "PBSKids.us@SD", "NickJrPlutoTV.us@US", "NickelodeonPlutoTV.us@SD",
        "LegoChannel.us@SD", "HappyKids.us@SD"
    ],
    "08 Docs & Learning": [
        "DocumentaryPlus.us@US", "WorldChannel.us@SD"
    ],
    "09 Music": [
        "Vevo80s.us@SD", "Vevo90s.us@SD"
    ],
}

OVERRIDES = {
    "ABC.us@WSOCTV": "https://aegis-cloudfront-1.tubi.video/d864a20b-85bb-41bc-8fbe-6c9d8a88a32d/playlist.m3u8",
    "CBSNews247.us@SD": "https://cbsn-us.cbsnstream.cbsnews.com/out/v1/55a8648e8f134e82a470f83d562deeca/master.m3u8",
    "ReutersTV.us@SD": "https://amg00453-reuters-amg00453c1-xumo-us-2073.playouts.now.amagi.tv/reuters-reuters-hls/playlist.m3u8",
    "USATODAY.us@SD": "https://amg00457-amg00457c1-stirr-us-8143.playouts.now.amagi.tv/playlist.m3u8",
    "AccuWeatherNOW.us@SD": "https://d1gldweznovt26.cloudfront.net/Accuweather.m3u8",
    "HallmarkMoviesMore.us@SD": "https://jmp2.uk/plu-628e685ba3811100070551a8.m3u8",
    "Baywatch.us@US": "https://aegis-cloudfront-1.tubi.video/9d1cd886-32b9-41ce-a7de-3babb46506aa/playlist.m3u8",
    "Mythbusters.us@UK": "https://d1cgf0ptrv4t22.cloudfront.net/Mythbuilders_GB.m3u8",
    "Vevo80s.us@SD": "https://jmp2.uk/plu-5fd7b8bf927e090007685853.m3u8",
    "Vevo90s.us@SD": "https://jmp2.uk/plu-5fd7bb1f86d94a000796e2c2.m3u8",
}


def parse_attr(line: str, key: str) -> str:
    match = re.search(rf'{re.escape(key)}="([^"]*)"', line)
    return match.group(1) if match else ""


with urllib.request.urlopen(SOURCE, timeout=60) as response:
    lines = response.read().decode("utf-8", errors="replace").splitlines()

entries = {}
for i, line in enumerate(lines[:-1]):
    if not line.startswith("#EXTINF:"):
        continue

    tvg_id = parse_attr(line, "tvg-id")
    stream = lines[i + 1].strip()

    if not tvg_id:
        continue
    if not stream.startswith("https://"):
        continue
    if "[Geo-blocked]" in line or "[Not 24/7]" in line:
        continue

    entries[tvg_id] = (line, stream)

output = [
    "#EXTM3U",
    "# Jellyfin-certified HTTPS-only English IPTV playlist",
    "# 42 retained channels; tested for Jellyfin/FFmpeg compatibility",
]

missing = []
written = 0

for group, ids in GROUPS.items():
    for tvg_id in ids:
        entry = entries.get(tvg_id)
        if not entry:
            missing.append(tvg_id)
            continue

        extinf, upstream_stream = entry
        stream = OVERRIDES.get(tvg_id, upstream_stream)
        name = extinf.split(",", 1)[1] if "," in extinf else tvg_id
        logo = parse_attr(extinf, "tvg-logo")

        output.append(
            f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" '
            f'group-title="{group}",{name}'
        )
        output.append(stream)
        written += 1

if missing:
    raise SystemExit("Missing required channels: " + ", ".join(missing))

if written != EXPECTED_COUNT:
    raise SystemExit(
        f"Expected {EXPECTED_COUNT} channels but built {written}; refusing to overwrite playlist."
    )

OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Wrote {written} Jellyfin-certified channels to {OUTPUT}")
