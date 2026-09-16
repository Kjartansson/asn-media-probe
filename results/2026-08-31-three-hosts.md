# Per-platform sweep, three hosts, 2026-08-31

Three vantage points, same URLs, same format selector, same `yt-dlp` version:

- **hel** — Hetzner dedicated, Helsinki
- **dk** — ordinary shared hosting, Denmark (a *datacenter* host, not residential)
- **res** — residential connection

| platform | hel | dk | res | verdict |
|---|---|---|---|---|
| facebook | 1280p, **no audio** | 2560p + audio | 2560p + audio | degraded |
| dailymotion | 2 formats, **480p** | 4 formats, 1080p | 4 formats, 1080p | degraded |
| youtube | bot-gated, or 360p when through | 2160p | 2160p | degraded |
| instagram | stripped, per-post | audio ✓ | — | degraded |
| twitter | 3840p (n=36) | 3840p (n=41) | — | not degraded |
| pinterest | 1920p | 1280p | — | not degraded |
| tiktok | 16 formats, 1920p, audio | identical | identical | not degraded |
| vk | 52 formats, 1080p, 11 audio tracks | identical | identical | not degraded |
| twitch | 7 formats, 1080p | identical | identical | not degraded (`acodec` unset everywhere) |

**dk and res measured identical on every platform.** Only the Helsinki address
is degraded. This is the result that rules out the obvious explanation:
if the mechanism were "datacenter bad, residential good", dk would look like
hel. It looks like res.

## The Facebook case in bytes

Same reel, same selector:

| vantage | bytes | streams |
|---|---|---|
| hel | 399,538 | h264 video only — **silent** |
| dk | 1,116,363 | vp9 + aac |
| res | 1,116,363 | vp9 + aac |

Extraction reported success, at full height, on all three.

## URLs are not IP-bound

Same address, same post, same `sd` format:

| URL obtained from | bytes | audio |
|---|---|---|
| hel | 2,154,715 | none |
| dk | 2,344,345 | aac |

Both fetched *from* hel. So the degradation attaches to the manifest request,
not to the media fetch — which means only extraction has to move, and delivery
can stay client-direct.

## IPv6 changes nothing

hel has working global IPv6. Same post over v4 and v6: byte-identical at
2,154,715 bytes, no audio either way.
