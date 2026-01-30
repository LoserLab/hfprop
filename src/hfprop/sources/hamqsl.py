"""HamQSL Solar XML feed parser.

Data provided by N0NBH at hamqsl.com.
Rate limit: no more than once per hour.
Attribution required: credit N0NBH.
"""

import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

from hfprop.config import HAMQSL_CACHE_TTL, HAMQSL_URL, HTTP_TIMEOUT, USER_AGENT
from hfprop.models import (
    BandCondition,
    BandForecast,
    GeomagStatus,
    PropagationReport,
    SolarData,
)
from hfprop.sources.base import DataSource


class HamQSLSource(DataSource):
    name = "N0NBH Solar Data (hamqsl.com)"
    cache_key = "hamqsl"
    cache_ttl_seconds = HAMQSL_CACHE_TTL

    def fetch_raw(self) -> bytes:
        req = Request(HAMQSL_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return resp.read()

    def parse(self, raw_data: bytes) -> PropagationReport:
        root = ET.fromstring(raw_data)
        sd = root.find(".//solardata")
        if sd is None:
            sd = root

        solar = SolarData(
            solar_flux=_int(sd, "solarflux"),
            sunspot_number=_int(sd, "sunspots"),
            a_index=_int(sd, "aindex"),
            k_index=_int(sd, "kindex"),
            xray=sd.findtext("xray", "N/A"),
            geomag_field=_geomag(sd.findtext("geomagfield", "")),
            signal_noise=sd.findtext("signalnoise", "N/A"),
            solar_wind=_float(sd, "solarwind"),
            bz=_float(sd, "magneticfield"),
            proton_flux=_float(sd, "protonflux"),
            updated=sd.findtext("updated", None),
        )

        bands = _parse_bands(root)

        return PropagationReport(
            solar=solar,
            bands=bands,
            source="Solar data courtesy N0NBH (hamqsl.com)",
        )


def _int(el, tag: str, default: int = 0) -> int:
    text = el.findtext(tag, "")
    try:
        return int(text)
    except ValueError:
        return default


def _float(el, tag: str):
    text = el.findtext(tag, "")
    try:
        return float(text)
    except ValueError:
        return None


def _geomag(text: str) -> GeomagStatus:
    text = text.strip().upper()
    for status in GeomagStatus:
        if status.value == text:
            return status
    return GeomagStatus.UNKNOWN


def _condition(text: str) -> BandCondition:
    text = (text or "").strip().capitalize()
    for cond in BandCondition:
        if cond.value == text:
            return cond
    return BandCondition.UNKNOWN


def _parse_bands(root) -> list:
    bands = []
    # Try calculatedconditions first, then look for band elements directly
    calc = root.find(".//calculatedconditions")
    if calc is None:
        return bands

    band_data = {}
    for band_el in calc.findall("band"):
        name = band_el.get("name", "")
        time = band_el.get("time", "day")
        condition = _condition(band_el.text)
        if name not in band_data:
            band_data[name] = {"day": BandCondition.UNKNOWN, "night": BandCondition.UNKNOWN}
        band_data[name][time] = condition

    for name, conds in band_data.items():
        bands.append(BandForecast(
            band_name=name,
            day=conds["day"],
            night=conds["night"],
        ))
    return bands
