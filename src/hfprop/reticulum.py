"""Reticulum network integration for hfprop.

Requires optional dependencies: rns, lxmf
Install with: pip install hfprop[reticulum]
"""

import json
import sys
import time

try:
    import RNS
    HAS_RNS = True
except ImportError:
    HAS_RNS = False

try:
    import LXMF
    HAS_LXMF = True
except ImportError:
    HAS_LXMF = False


def check_rns_available():
    """Exit with helpful message if RNS is not installed."""
    if not HAS_RNS:
        print(
            "Reticulum (rns) is not installed.\n"
            "Install with: pip install hfprop[reticulum]",
            file=sys.stderr,
        )
        sys.exit(1)


def report_to_json(report) -> bytes:
    """Serialize a PropagationReport to JSON bytes for network transport."""
    data = {
        "solar": {
            "solar_flux": report.solar.solar_flux,
            "sunspot_number": report.solar.sunspot_number,
            "a_index": report.solar.a_index,
            "k_index": report.solar.k_index,
            "xray": report.solar.xray,
            "geomag_field": report.solar.geomag_field.value,
            "signal_noise": report.solar.signal_noise,
            "assessment": report.solar.conditions_summary(),
        },
        "bands": [
            {"name": b.band_name, "day": b.day.value, "night": b.night.value}
            for b in report.bands
        ],
        "source": report.source,
    }
    return json.dumps(data).encode("utf-8")


class HFPropService:
    """Reticulum destination that serves propagation data on request."""

    APP_NAME = "hfprop"
    ASPECT = "propagation"

    def __init__(self, offline=False):
        check_rns_available()
        self.offline = offline
        self.reticulum = RNS.Reticulum()
        self.identity = RNS.Identity()
        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            self.APP_NAME,
            self.ASPECT,
        )
        self.destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
        self.destination.register_request_handler(
            "/propagation/data",
            response_generator=self._handle_request,
            allow=RNS.Destination.ALLOW_ALL,
        )

    def _handle_request(self, path, data, request_id, link_id, remote_identity, requested_at):
        from hfprop.fetch import get_report
        try:
            report = get_report(offline=self.offline)
            return report_to_json(report)
        except SystemExit:
            return json.dumps({"error": "No data available"}).encode()

    def announce(self):
        self.destination.announce()

    def get_hash(self) -> str:
        return RNS.prettyhexrep(self.destination.hash)

    def run_forever(self, announce_interval=600):
        print(f"hfprop serve running. Destination: {self.get_hash()}")
        print(f"Announcing every {announce_interval}s. Ctrl+C to stop.")
        self.announce()
        try:
            while True:
                time.sleep(announce_interval)
                self.announce()
        except KeyboardInterrupt:
            print("\nService stopped.")


class HFPropClient:
    """Query a remote hfprop serve node."""

    APP_NAME = "hfprop"
    ASPECT = "propagation"

    def __init__(self):
        check_rns_available()
        self.reticulum = RNS.Reticulum()
        self.identity = RNS.Identity()

    def query(self, destination_hash_hex, timeout=30):
        """Query a remote node and return parsed JSON dict, or None on failure."""
        dest_hash = bytes.fromhex(destination_hash_hex.replace(":", "").replace(" ", ""))

        if not RNS.Transport.has_path(dest_hash):
            RNS.Transport.request_path(dest_hash)
            start = time.time()
            while not RNS.Transport.has_path(dest_hash) and time.time() - start < timeout:
                time.sleep(0.5)

        if not RNS.Transport.has_path(dest_hash):
            return None

        dest_identity = RNS.Identity.recall(dest_hash)
        if dest_identity is None:
            return None

        destination = RNS.Destination(
            dest_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            self.APP_NAME,
            self.ASPECT,
        )

        link = RNS.Link(destination)
        start = time.time()
        while link.status != RNS.Link.ACTIVE and time.time() - start < timeout:
            time.sleep(0.1)

        if link.status != RNS.Link.ACTIVE:
            link.teardown()
            return None

        receipt = link.request(
            "/propagation/data",
            data=None,
        )

        start = time.time()
        while receipt.status == RNS.RequestReceipt.SENT and time.time() - start < timeout:
            time.sleep(0.1)

        if receipt.status == RNS.RequestReceipt.DELIVERED:
            response = receipt.response
            if response:
                return json.loads(response)

        link.teardown()
        return None
