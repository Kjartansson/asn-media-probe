# asn-media-probe

Compare what a media platform serves to different source IPs.

Platforms vary what they hand back based on the reputation of the requesting
address. Not by blocking it — by quietly serving a worse manifest. You get a
`200`, full resolution, no error, and no audio track.

That failure mode is hard to notice because every signal you would normally
watch reads as healthy. This tool runs one extraction from several vantage
points and diffs the results.

## Usage

```
./probe.py <url> --via local --via ssh:my-other-box
```

```
vantage       fmts  max h  audio  cdn host
------------  ----  -----  -----  ------------------------
local           12   1280     NO  video-hel3-1.xx.fbcdn.net
ssh:other        9   2560    yes  video-cph2-1.xx.fbcdn.net

DISAGREEMENT: no audio offered to local, but offered elsewhere.
The manifest differs by source IP. Changing the format selector will not help.
```

Exits `1` on disagreement, so it works as a scheduled canary and not only as a
one-off diagnostic.

Requires `yt-dlp` on each vantage point. `ssh:` vantages use `BatchMode`, so
key auth must already work.

## What it measures

Per vantage point: how many formats were offered, the maximum height among
them, whether **any** format declares a real audio codec, and the CDN hostname
of the chosen URL. The CDN host is usually the tell — it names the edge that
answered, which is what actually differs.

The audio check deliberately does not claim much on its own. `NO` means
"nothing on offer here declares an audio codec", and on platforms whose
progressive formats leave `acodec` unset that is the normal reading at *every*
vantage point. This is why the tool compares vantage points against each other
rather than treating `NO` as a fault in isolation.

## Contributing a datapoint

A single vantage point proves nothing on its own — `audio NO` only means
something next to another vantage point reporting `yes` for the same URL. The
useful thing is coverage across providers.

There is a manual-dispatch GitHub Actions workflow
([`.github/workflows/probe.yml`](.github/workflows/probe.yml)) that runs the
probe from a hosted runner and reports the runner's egress IP and ASN in the
job summary. Hosted runners egress from Microsoft/Azure ranges, so it
contributes a large-cloud datapoint without renting anything; fork it and it
reports from whatever your runner sits on.

It is dispatch-only by design. A scheduled job would mean this repo quietly
making automated requests to a platform on a timer, which is neither necessary
nor polite.

If you get a result worth recording, open a PR adding it to `results/`.

## Findings

[`results/`](results/) has measured sweeps. The short version, from three hosts
in August and September 2026:

- **Meta (Facebook/Instagram) omits the audio representation entirely** from
  the manifest served to certain addresses. Not a selector problem — the format
  list contains no audio-bearing entry at all, so `sd` and `hd` are both silent.
- **It is not datacenter-versus-residential.** An ordinary shared-hosting box in
  Denmark receives audio; a Hetzner box in Helsinki does not. It tracks the
  specific address and its ASN.
- **Dailymotion truncates the format ladder** for the same address — two formats
  topping out at 480p, against four reaching 1080p elsewhere.
- **The URLs are not IP-bound.** Fetching a relay-obtained URL *from* the
  degraded address returns the full bytes, audio included. Only extraction has
  to move.
- **IPv6 makes no difference.** Same post over v4 and v6 from a host with
  working global v6: byte-identical, silent both ways.

## Why this exists

It came out of running [voomreel.com](https://voomreel.com), where a user
reported a video that played with sound on their phone and downloaded silent.
Every metric said the extraction had succeeded, at full 2560p, on every host.

The write-up of what that cost to find — two wrong fixes, and why the second
wrong one was the interesting one — is here:
**[The signal that could only be refreshed by using it](https://voomreel.com/guides/silent-degradation)**.

## License

MIT
