# Movie Vault EPG coverage audit

Audited against the 67-channel authorized playlist and the iptv-org EPG site catalog on 2026-10-13. The playlist was not changed. A mapping is accepted only when the station/feed identity or provider channel ID is exact.

## Resolved in this change

| Playlist channel | Gap cause | Resolution |
| --- | --- | --- |
| ABC WSOC-TV | Naming mismatch | Map the playlist ID to TV Passport's exact WSOC Charlotte HD station. |
| beIN SPORTS XTRA | Upstream availability | Existing exact mapping returned programs on the fresh validation run. |
| NFL Channel | Missing mapping | Add the exact Pluto channel ID used by the playlist stream. |
| MLB | Missing mapping | Add the exact Pluto channel ID used by the playlist stream. |
| Monster Jam | Missing XMLTV identity | Add the exact Pluto Canada channel ID even though the upstream catalog leaves `xmltv_id` blank. |
| 00s Replay | Missing XMLTV identity | Add the exact Pluto US channel ID even though the upstream catalog leaves `xmltv_id` blank. |
| Pluto TV Sci-Fi | Missing mapping | Add the exact Pluto Canada channel ID used by the playlist stream. |
| Pluto TV Westerns | Missing mapping | Add the exact Pluto US channel ID used by the playlist stream. |
| Cheers | Missing XMLTV identity | Add the exact Pluto Canada channel ID even though the upstream catalog leaves `xmltv_id` blank. |
| Star Trek: The Next Generation | Missing XMLTV identity | Add the exact Pluto US channel ID even though the upstream catalog leaves `xmltv_id` blank. |

## Unresolved safely

| Playlist channel | Gap cause | Reason not mapped |
| --- | --- | --- |
| Reuters TV | Unavailable exact upstream schedule | Available listings are for Reuters 60, not this Reuters TV feed. |
| ACC Digital Network | Unverified cross-provider mapping | Catalog schedules exist on Plex, Roku, and Xumo, but the playlist is an Amazon/Amagi feed. |
| World Poker Tour | Unverified cross-provider mapping | Several provider schedules exist, but none identifies the playlist's scheduler feed. |
| DUST | Unverified cross-provider mapping | Listings exist for Samsung/tvtv feeds; the playlist feed cannot be tied to either. |
| AFV | Unavailable exact upstream schedule | Plex lists an AFV schedule without a confirmed identity for this Frequency feed. |
| Lego Channel | Unavailable exact upstream schedule | Catalog entries are regional Samsung or LEGO Kids TV feeds, not a confirmed match. |
| HappyKids | Unavailable exact upstream schedule | Only regional Samsung entries were found; the playlist feed is not identified. |
| Super Simple Songs | Upstream schedule unavailable | The exact Roku listing timed out and produced no validated XMLTV data. |
| pocket.watch | Unavailable exact upstream schedule | Plex/Roku candidates exist but cannot be tied to this specific Game On feed. |
| BBC Home & Garden | Unverified cross-provider mapping | Plex/Xumo schedules exist but the playlist's CloudFront feed is not identified. |
| Localish | Unverified cross-provider mapping | A Roku schedule exists, but the playlist's Disney/CloudFront feed is not identified. |
| PBS Travel | Unverified cross-provider mapping | Plex/Roku schedules exist, but the playlist feed is not tied to either provider. |
| Antiques Road Trip | Unverified regional/feed match | The playlist is Samsung Australia; available identified schedules are other regions/providers. |
| XITE 90s Throwback | Unverified cross-provider mapping | A Plex schedule exists, but the playlist feed is not identified as Plex. |
| The Country Network | Unverified cross-provider mapping | A tvtv.us schedule exists, but the playlist uses a separate Amagi feed. |

Fresh validation result: **52/67 channels**, up from **42/67** in the deployed guide. The validated XMLTV contained 3,446 program records across the full guide build.
