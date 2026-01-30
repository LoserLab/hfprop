"""Tests for HamQSL XML feed parser."""

from hfprop.models import BandCondition, GeomagStatus
from hfprop.sources.hamqsl import HamQSLSource


def test_parse_solar_flux(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.solar_flux == 129


def test_parse_sunspot_number(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.sunspot_number == 117


def test_parse_k_index(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.k_index == 3


def test_parse_a_index(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.a_index == 22


def test_parse_xray(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.xray == "C1.0"


def test_parse_geomag_field(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.geomag_field == GeomagStatus.UNSETTLED


def test_parse_signal_noise(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.signal_noise == "S2-S3"


def test_parse_solar_wind(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.solar_wind == 578.3


def test_parse_bz(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.bz == -1.3


def test_parse_proton_flux(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert report.solar.proton_flux == 11.0


def test_parse_band_count(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert len(report.bands) == 4


def test_parse_band_80m_40m(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    band = next(b for b in report.bands if b.band_name == "80m-40m")
    assert band.day == BandCondition.POOR
    assert band.night == BandCondition.FAIR


def test_parse_band_30m_20m(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    band = next(b for b in report.bands if b.band_name == "30m-20m")
    assert band.day == BandCondition.GOOD
    assert band.night == BandCondition.GOOD


def test_parse_band_12m_10m(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    band = next(b for b in report.bands if b.band_name == "12m-10m")
    assert band.day == BandCondition.FAIR
    assert band.night == BandCondition.POOR


def test_source_attribution(hamqsl_xml):
    report = HamQSLSource().parse(hamqsl_xml)
    assert "N0NBH" in report.source


def test_parse_minimal_xml():
    xml = b"""<?xml version="1.0"?>
    <solar><solardata>
        <solarflux>100</solarflux>
        <sunspots>50</sunspots>
        <aindex>10</aindex>
        <kindex>2</kindex>
        <xray>B1.0</xray>
        <geomagfield>QUIET</geomagfield>
        <signalnoise>S1</signalnoise>
    </solardata></solar>"""
    report = HamQSLSource().parse(xml)
    assert report.solar.solar_flux == 100
    assert report.solar.solar_wind is None
    assert report.bands == []


def test_parse_bad_values():
    xml = b"""<?xml version="1.0"?>
    <solar><solardata>
        <solarflux>bad</solarflux>
        <sunspots></sunspots>
        <aindex>10</aindex>
        <kindex>2</kindex>
        <xray>B1.0</xray>
        <geomagfield>WEIRD</geomagfield>
        <signalnoise>S1</signalnoise>
    </solardata></solar>"""
    report = HamQSLSource().parse(xml)
    assert report.solar.solar_flux == 0  # default on bad parse
    assert report.solar.sunspot_number == 0
    assert report.solar.geomag_field == GeomagStatus.UNKNOWN
