# Azure is not degraded — 2026-09-16

Same Facebook reel, same day, four vantage points.

| vantage | ASN | formats | max h | audio | CDN edge |
|---|---|---|---|---|---|
| Hetzner, Helsinki | AS24940 | — | 1280 | **no** | `video-hel3-1` |
| GitHub Actions runner | AS8075 Microsoft | 11 | 2560 | yes | `video-ord5-1` |
| Danish shared hosting | — | 11 | 2560 | yes | `video-cph2-1` |
| residential | — | 11 | 2560 | yes | `video.fcph4-1` |

The Azure row was produced by `.github/workflows/probe.yml` from egress
`20.84.47.35`, which `ipinfo.io` reports as `AS8075 Microsoft Corporation`.
The residential row is the same URL probed the same hour.

## Why this matters

The intuitive explanations are all wrong, and each one dies to a row above:

- **"Datacenter versus residential"** — the Danish host is a datacenter.
- **"Cloud providers are flagged as a class"** — Azure is about as
  large-cloud as an address gets, and it is served full audio. Published work
  on Meta's enforcement describes hosting ASNs (AWS, GCP, Azure, Hetzner, OVH,
  DigitalOcean) being flagged by range, but that literature is about login and
  API access. Whatever drives the manifest difference, it does not treat
  "large cloud" as one category.
- **"Geography"** — the working vantage points answered from Chicago,
  Copenhagen and Copenhagen. The failing one answered from Helsinki, but the
  Danish host is closer to Helsinki than Chicago is.

What is left is the specific range. Of four ASNs measured, exactly one is
degraded.

## What this does not establish

n=1 per provider, one platform, one URL, one day. In particular **DigitalOcean
is untested** — it is grouped with Hetzner in the literature above, but so is
Azure, and Azure is fine here. Assume nothing about a provider you have not
measured. That is the entire point of the tool.

Contributions of further vantage points are welcome; see the README.
