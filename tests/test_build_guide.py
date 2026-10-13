import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_guide


class BuildGuideTests(unittest.TestCase):
    def test_playlist_and_epg_coverage_fields(self):
        playlist = '#EXTM3U\n#EXTINF:-1 tvg-id="One.us" group-title="02 News",One\nhttps://example.com/live.m3u8\n'
        xml = '''<?xml version="1.0"?><tv date="20261013">
          <programme start="20261013120000 +0000" stop="20261013130000 +0000" channel="One.us"><title>News</title></programme>
        </tv>'''
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "playlist.m3u").write_text(playlist, encoding="utf-8")
            (base / "guide.xml").write_text(xml, encoding="utf-8")
            output = base / "channels.json"
            argv = ["build_guide.py", "--playlist", str(base / "playlist.m3u"), "--epg", str(base / "guide.xml"), "--output", str(output)]
            with patch("sys.argv", argv):
                build_guide.main()
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["channelCount"], 1)
        self.assertEqual(payload["epgChannelCount"], 1)
        self.assertEqual(payload["epgMissingCount"], 0)
        self.assertEqual(payload["channels"][0]["programs"][0]["title"], "News")


if __name__ == "__main__":
    unittest.main()
