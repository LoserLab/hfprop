"""Configuration constants for hfprop."""

# API endpoints
HAMQSL_URL = "https://www.hamqsl.com/solarxml.php"
SWPC_KINDEX_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
SWPC_FLUX_URL = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"
SWPC_FORECAST_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"

# Cache TTLs (seconds)
HAMQSL_CACHE_TTL = 3600  # 1 hour (rate limit compliance)
SWPC_CACHE_TTL = 900  # 15 minutes

# HTTP
USER_AGENT = "hfprop/0.1.0 (+https://github.com/LFManifesto/hfprop)"
HTTP_TIMEOUT = 15

# FreeDV modes available in ReticulumHF
FREEDV_MODES = {
    "DATAC1": {"bps": 290, "min_snr_db": 5, "label": "Fastest, needs good conditions"},
    "DATAC3": {"bps": 124, "min_snr_db": 0, "label": "Balanced speed/robustness"},
    "DATAC4": {"bps": 87, "min_snr_db": -4, "label": "Most robust, slowest"},
}

# Band definitions
HF_BANDS = {
    "80m-40m": {
        "freq_range": "3.5-7.3 MHz",
        "character": "NVIS / Regional",
        "note": "Best for short-range NVIS links (<500km)",
    },
    "30m-20m": {
        "freq_range": "10.1-14.3 MHz",
        "character": "Mid-range / DX",
        "note": "Primary DX bands. 20m often best daytime choice.",
    },
    "17m-15m": {
        "freq_range": "18.1-21.4 MHz",
        "character": "DX",
        "note": "Excellent when open. Solar-cycle dependent.",
    },
    "12m-10m": {
        "freq_range": "24.9-29.7 MHz",
        "character": "DX / Sporadic",
        "note": "Unreliable. Best during solar maximum.",
    },
}

# SFI thresholds for human-readable assessment
SFI_THRESHOLDS = [
    (70, "Low"),
    (120, "Moderate"),
    (200, "High"),
    (float("inf"), "Very High"),
]

# K-index thresholds
K_THRESHOLDS = [
    (1, "Quiet"),
    (3, "Unsettled"),
    (4, "Active"),
    (5, "Minor Storm"),
    (6, "Moderate Storm"),
    (7, "Strong Storm"),
    (9, "Extreme Storm"),
]
