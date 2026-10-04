#!/usr/bin/env python3
"""Validate that guide.xml is parseable, identity-safe, and useful."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def xmltv_time(value: str) -> dt.datetime:
    match = re.fullmatch(r"(\d{14})\s+([+-]\d{4})", value)
    if not match:
        raise ValueError(f"unsupported XMLTV timestamp: {value!r}")
    return dt.datetime.strptime(" ".join(match.groups()), "%Y%m%d%H%M%S %z")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("guide", type=Path)
    parser.add_argument("--minimum-channels", type=int, default=1)
    args = parser.parse_args()

    root = ET.parse(args.guide).getroot()
    if root.tag != "tv":
        raise ValueError("root element is not <tv>")

    channels = {node.attrib["id"] for node in root.findall("channel")}
    now = dt.datetime.now(dt.timezone.utc)
    future = {}
    for programme in root.findall("programme"):
        channel = programme.attrib["channel"]
        stop = xmltv_time(programme.attrib["stop"])
        if channel not in channels:
            raise ValueError(f"programme references missing channel {channel}")
        if stop > now:
            future[channel] = future.get(channel, 0) + 1

    if len(future) < args.minimum_channels:
        raise ValueError(
            f"only {len(future)} channels have future programmes; expected at least {args.minimum_channels}"
        )
    print(f"valid XMLTV: {len(channels)} channels, {sum(future.values())} future programmes on {len(future)} channels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
