# Jellyfin XMLTV guide

`epg.channels.xml` maps the playlist's iptv-org `tvg-id` values to exact listings records from iptv-org's maintained EPG grabber. `refresh_epg.sh` fetches three days of listings, validates the XML and future-program coverage, then atomically replaces `guide.xml`.

Run a refresh manually:

```sh
./epg/refresh_epg.sh
```

The included user timer runs at approximately 04:15 and 16:15 America/New_York daily. A loopback-only HTTP service exposes the guide to Jellyfin at `http://127.0.0.1:9988/guide.xml`; it does not expose the guide on the LAN. The existing M3U tuner is unchanged.

No verified iptv-org guide record currently exists for these playlist IDs, so they are intentionally omitted instead of receiving guessed schedules:

- `ABC.us@WSOCTV`
- `ReutersTV.us@SD`
- `00sReplay.us@SD`
- `Cheers.us@CA`
- `AFV.us@SD`
- `LegoChannel.us@SD`
- `HappyKids.us@SD`

The source configuration contains 43 mapped channels out of the validated 50-channel playlist. A refresh may yield fewer channels if an upstream listings provider is temporarily unavailable; validation requires at least 35 channels with future programmes before replacing the last known-good guide.
