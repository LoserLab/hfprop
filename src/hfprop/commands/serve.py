"""hfprop serve -- Run as a Reticulum propagation service."""


def run(args):
    from hfprop.reticulum import HFPropService
    service = HFPropService(offline=args.offline)
    announce_interval = getattr(args, "announce_interval", 600)
    service.run_forever(announce_interval=announce_interval)
