#!/usr/bin/env python3
"""Build the Movie Vault guide data from the authorized M3U and XMLTV files."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
CATEGORY_MAP = {
    "01 Local Carolinas": "Local",
    "02 News": "News",
    "03 Weather & Business": "News",
    "04 Sports": "Sports",
    "05 Movies": "Movies",
    "06 TV & Comedy": "Entertainment",
    "07 Kids & Family": "Kids",
    "08 Docs & Learning": "Entertainment",
    "09 Music": "Entertainment",
}


def read_text(source: str) -> str:
    if source.startswith(("https://", "http://")):
        with urllib.request.urlopen(source, timeout=60) as response:
            return response.read().decode("utf-8-sig")
    return Path(source).read_text(encoding="utf-8-sig")


def parse_playlist(text: str) -> list[dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    channels = []
    for index, line in enumerate(lines):
        if not line.startswith("#EXTINF:") or index + 1 >= len(lines):
            continue
        attrs = dict(ATTR_RE.findall(line))
        stream = lines[index + 1]
        if not stream.startswith("https://"):
            raise ValueError(f"Non-HTTPS stream found for {attrs.get('tvg-id', 'unknown')}")
        name = line.split(",", 1)[1].strip() if "," in line else attrs.get("tvg-id", "Channel")
        source_group = attrs.get("group-title", "")
        channels.append({
            "number": len(channels) + 1,
            "id": attrs.get("tvg-id", ""),
            "name": name,
            "logo": attrs.get("tvg-logo", ""),
            "category": CATEGORY_MAP.get(source_group, "Entertainment"),
            "sourceCategory": source_group,
            "stream": stream,
            "programs": [],
        })
    return channels


def xmltv_time(value: str) -> str:
    parsed = datetime.strptime(value.strip(), "%Y%m%d%H%M%S %z")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_epg(path: str) -> tuple[dict[str, list[dict]], str]:
    root = ET.parse(path).getroot()
    programs: dict[str, list[dict]] = {}
    for item in root.findall("programme"):
        channel_id = item.get("channel", "")
        title = item.findtext("title", default="Program information unavailable").strip()
        subtitle = item.findtext("sub-title", default="").strip()
        description = item.findtext("desc", default="").strip()
        programs.setdefault(channel_id, []).append({
            "start": xmltv_time(item.get("start", "")),
            "stop": xmltv_time(item.get("stop", "")),
            "title": title,
            "subtitle": subtitle,
            "description": description,
        })
    for entries in programs.values():
        entries.sort(key=lambda entry: entry["start"])
    return programs, root.get("date", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playlist", default="English_TV_Essentials_US.m3u")
    parser.add_argument("--epg", required=True)
    parser.add_argument("--output", default="guide/data/channels.json")
    args = parser.parse_args()

    channels = parse_playlist(read_text(args.playlist))
    programs, epg_date = parse_epg(args.epg)
    for channel in channels:
        channel["programs"] = programs.get(channel["id"], [])

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "playlistSource": args.playlist,
        "epgDate": epg_date,
        "channelCount": len(channels),
        "epgChannelCount": sum(bool(channel["programs"]) for channel in channels),
        "channels": channels,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Built {len(channels)} channels; EPG coverage {payload['epgChannelCount']}/{len(channels)}")


if __name__ == "__main__":
    main()
