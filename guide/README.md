# Movie Vault Live TV guide

This is a separate, static dashboard for the existing authorized Movie Vault playlist. It does not replace or modify the playlist or player.

Build the guide data from the published playlist and the locally generated authorized XMLTV file:

```sh
python3 scripts/build_guide.py \
  --playlist https://raw.githubusercontent.com/JColeLatt/vlc-iptv-playlist/main/English_TV_Essentials_US.m3u \
  --epg epg/guide.xml \
  --output guide/data/channels.json
```

Serve the repository root over HTTP and open `/guide/`. Favorites remain in the browser through `localStorage`.
