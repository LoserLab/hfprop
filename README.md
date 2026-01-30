# hfprop

HF propagation conditions for field operators. A companion tool for [ReticulumHF](https://github.com/LFManifesto/ReticulumHF).

Check band conditions, solar indices, and get FreeDV mode recommendations from the terminal — no browser needed.

## Install

```bash
pip install .
```

Or in development:

```bash
pip install -e ".[dev]"
```

**Zero runtime dependencies.** Uses only the Python standard library. Works on Raspberry Pi.

## Usage

```bash
# Current conditions at a glance (default command)
hfprop now

# Band-by-band breakdown with FreeDV mode suggestions
hfprop bands

# Full solar/geomagnetic indices
hfprop solar

# Location-aware output (Maidenhead grid locator)
hfprop --grid EM73 now
hfprop --grid EM73 bands

# Point-to-point path analysis
hfprop path EM73 JN48

# Continuous monitoring (refreshes hourly, Ctrl+C to stop)
hfprop watch
hfprop watch --interval 1800

# Condition history (logged on every live fetch)
hfprop history
hfprop history --days 14
```

### Global Flags

```bash
hfprop --offline now       # Use cached data only (no network)
hfprop --json now          # JSON output for scripting/integration
hfprop --no-color now      # Disable ANSI colors
hfprop --grid EM73 now     # Location-aware (day/night/grayline)
```

### Example Output

```
HF Propagation -- 30 Jan 2026 16:27 UTC
==========================================
SFI: 129  |  SSN: 99  |  K: 2  |  A: 22
X-Ray: C1.0  |  Geomag: QUIET
Noise Floor: S1-S2
Location: EM73 -- DAY (elev: 35.5)

Assessment: GOOD - Normal propagation expected

Band        Day
--------------------
80m-40m     Fair
30m-20m     Good
17m-15m     Good
12m-10m     Fair

Data: Solar data courtesy N0NBH (hamqsl.com) | Cached: No
```

### Path Analysis

```
Path Analysis: EM73 -> JN48
=============================================

Route:    7,560 km  |  Bearing: 45  |  Type: Long-haul DX

Endpoint    Grid    Status      Elev
------------------------------------------
Local       EM73    DAY         +35.5
Remote      JN48    GRAYLINE    -4.7

  JN48 is in GRAYLINE. 80m-40m enhanced.

Recommended Bands (for 7,560 km):
  17m-15m     Day: Good      -> DATAC1 (290bps)
  12m-10m     Day: Fair      -> DATAC3 (124bps)
```

## Features

### Grid Locator Support (`--grid`)

Pass your Maidenhead grid square to get location-aware output. The tool calculates solar elevation to determine if it's day, night, or grayline at your location, and filters the band table to show only the relevant conditions.

### Grayline Detection

When your location is in civil twilight (-6° to 0° solar elevation), the tool displays a grayline indicator. Grayline conditions enhance 80m-40m propagation due to reduced D-layer absorption.

### Point-to-Point Path Analysis (`path`)

Analyze propagation between two stations. Computes great-circle distance and bearing, checks solar status at both endpoints, and recommends bands and FreeDV modes based on distance and conditions.

### Watch Mode (`watch`)

Continuously monitors conditions with automatic refresh. Detects and highlights changes between cycles (K-index shifts, band condition changes).

### Condition History (`history`)

Every live data fetch is automatically logged to a local SQLite database (`~/.local/share/hfprop/history.db`). Review past conditions to identify patterns and plan communication windows.

### Reticulum Network Service (`serve` / `query`)

Expose propagation data over Reticulum mesh networks. Nodes with internet access can serve current conditions to nodes without internet.

```bash
# Install with Reticulum support
pip install ".[reticulum]"

# Serve propagation data on the mesh
hfprop serve

# Query a remote hfprop node
hfprop query <destination_hash>
```

## Data Sources

| Source | What | Update Rate |
|--------|------|-------------|
| [HamQSL](https://www.hamqsl.com/solar.html) (N0NBH) | Solar indices + band conditions | Hourly |
| [NOAA SWPC](https://www.swpc.noaa.gov/) | K-index, solar flux | Minutes |

## Offline Mode

Run `hfprop` once with internet to populate the cache (`~/.cache/hfprop/`). After that, `hfprop --offline` works without network access — useful in the field.

## ReticulumHF Integration

The `bands` and `path` commands suggest FreeDV modes (DATAC1/3/4) based on current band conditions:

- **DATAC1** (290 bps, 5 dB SNR) — recommended when conditions are Good
- **DATAC3** (124 bps, 0 dB SNR) — recommended when conditions are Fair
- **DATAC4** (87 bps, -4 dB SNR) — recommended when conditions are Poor

The `--json` flag outputs structured data for programmatic integration.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT — see [LICENSE](LICENSE).

Solar data courtesy [N0NBH](https://www.hamqsl.com/solar.html). Geomagnetic data from [NOAA SWPC](https://www.swpc.noaa.gov/).
