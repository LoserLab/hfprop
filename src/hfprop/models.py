"""Data models for hfprop."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from hfprop.config import K_THRESHOLDS, SFI_THRESHOLDS


class BandCondition(Enum):
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    UNKNOWN = "Unknown"


class GeomagStatus(Enum):
    QUIET = "QUIET"
    UNSETTLED = "UNSETTLD"
    ACTIVE = "ACTIVE"
    STORM = "STORM"
    MAJOR_STORM = "MAJOR"
    UNKNOWN = "UNKNOWN"


@dataclass
class SolarData:
    solar_flux: int
    sunspot_number: int
    a_index: int
    k_index: int
    xray: str
    geomag_field: GeomagStatus
    signal_noise: str
    solar_wind: Optional[float] = None
    bz: Optional[float] = None
    proton_flux: Optional[float] = None
    updated: Optional[str] = None

    def conditions_summary(self) -> str:
        if self.k_index >= 5:
            return "DISTURBED - HF severely degraded"
        elif self.k_index >= 4:
            return "UNSETTLED - HF may be degraded"
        elif self.solar_flux >= 150 and self.k_index <= 2:
            return "EXCELLENT - Strong propagation likely"
        elif self.solar_flux >= 100:
            return "GOOD - Normal propagation expected"
        else:
            return "FAIR - Lower bands favored"

    def sfi_label(self) -> str:
        for threshold, label in SFI_THRESHOLDS:
            if self.solar_flux < threshold:
                return label
        return "Unknown"

    def k_label(self) -> str:
        for threshold, label in K_THRESHOLDS:
            if self.k_index <= threshold:
                return label
        return "Extreme Storm"


@dataclass
class BandForecast:
    band_name: str
    day: BandCondition
    night: BandCondition


@dataclass
class PropagationReport:
    solar: SolarData
    bands: List[BandForecast] = field(default_factory=list)
    source: str = ""
    fetched_at: Optional[datetime] = None
    cached: bool = False
