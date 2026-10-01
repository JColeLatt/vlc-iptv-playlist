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

with urllib.request.urlopen(SOURCE, timeout=60) as response:
 lines = response.read().decode("utf-8", errors="replace").splitlines()

entries = {}
for i, line in enumerate(lines[:-1]):
    if not line.startswith("#EXTINF:"):
        continue
 stream = lines[i + 1].strip()
 match = re.search(r'tvg-id="([^"]*)"', line)
    if not match:
        continue
 tvg_id = match.group(1)
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
for group, ids in GROUPS.items():
    for tvg_id in ids:
 entry = entries.get(tvg_id)
        if not entry:
 missing.append(tvg_id)
            continue
        extinf, stream = entry
 ame = extinf.split(",", 1)[1]
 logo_match = re.search(r'tvg-logo="([^"]*)"', extinf)
 logo = logo_match.group(1) if logo_match else ""
 output.append(
            f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{ ame}'
        )
 output.append(stream)

if missing:
    raise SystemExit("Missing required channels: " + ", ".join(missing))

OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Wrote {sum(len(v) for v in GROUPS.values())} channels to {OUTPUT}")
