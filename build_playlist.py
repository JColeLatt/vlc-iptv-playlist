import re
import urllib.request
from pathlib import Path

SOURCE = "https://iptv-org.github.io/iptv/languages/eng.m3u"
OUTPUT = Path("English_TV_Essentials_US.m3u")

GROUPS = {
    "01 Local Carolinas": [
        "ABC.us@WSOCTV", "WBTV641.us@HD", "ABC.us@WLOS"
    ],
    "02 News": [
        "ABCNewsLive.us@SD", "CBSNews247.us@SD", "NBCNewsNOW.us@SD",
        "ScrippsNews.us@SD", "ReutersTV.us@SD", "LiveNOWfromFOX.us@SD",
        "USATODAY.us@SD", "CheddarNews.us@SD"
    ],
    "03 Weather & Business": [
        "AccuWeatherNOW.us@SD", "FoxWeather.us@SD", "WeatherNation.us@SD",
        "YahooFinance.us@SD", "SchwabNetwork.us@SD"
    ],
    "04 Sports": [
        "CBSSportsHQ.us@SD", "CBSSportsGolazoNetwork.us@SD",
        "NBCSportsNOW.us@SD", "FuboSportsNetwork.us@SD", "PGATour.us@SD",
        "SportsGrid.us@SD", "Pac12Insider.us@SD", "PBRRidePass.us@SD"
    ],
    "05 Movies": [
        "00sReplay.us@SD", "70sCinema.us@SD", "80sRewind.us@SD",
        "90sThrowback.us@SD", "HallmarkMoviesMore.us@SD", "MovieSphere.us@US",
        "PlutoTVActionMovies.us@CA", "PlutoTVComedyMovies.us@CA"
    ],
    "06 TV & Comedy": [
        "48Hours.us@US", "Baywatch.us@US", "Cheers.us@CA", "Frasier.us@CA",
        "HappyDays.us@SD", "Matlock.us@SD", "Mythbusters.us@UK",
        "NBCComedyVault.us@SD"
    ],
    "07 Kids & Family": [
        "PBSKids.us@SD", "NickJrPlutoTV.us@US", "NickelodeonPlutoTV.us@SD",
        "LegoChannel.us@SD", "HappyKids.us@SD"
    ],
    "08 Docs & Learning": [
        "DocumentaryPlus.us@US", "MagellanTVNow.us@SD", "WorldChannel.us@SD"
    ],
    "09 Music": [
        "Vevo80s.us@SD", "Vevo90s.us@SD"
    ],
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

    stream = lines[i + 1].strip()
    tvg_id = parse_attr(line, "tvg-id")

    if not tvg_id:
        continue
    if not stream.startswith("https://"):
        continue
    if "[Geo-blocked]" in line or "[Not 24/7]" in line:
        continue

    entries[tvg_id] = (line, stream)

output = [
    "#EXTM3U",
    "# Curated HTTPS-only English IPTV playlist for VLC",
    "# Auto-built from IPTV-org English playlist",
]

missing = []
written = 0

for group, ids in GROUPS.items():
    for tvg_id in ids:
        entry = entries.get(tvg_id)
        if not entry:
            missing.append(tvg_id)
            continue

        extinf, stream = entry
        name = extinf.split(",", 1)[1] if "," in extinf else tvg_id
        logo = parse_attr(extinf, "tvg-logo")

        output.append(
            f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" '
            f'group-title="{group}",{name}'
        )
        output.append(stream)
        written += 1

if written < 25:
    raise SystemExit(
        f"Only {written} curated channels matched; refusing to overwrite playlist."
    )

OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Wrote {written} channels to {OUTPUT}")

if missing:
    print("Skipped missing channels: " + ", ".join(missing))
