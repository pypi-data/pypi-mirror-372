"""Package entrypoint forwarding to :mod:`quantumscan.cli`."""

from .cli.__main__ import main


if __name__ == "__main__":  # pragma: no cover - simple forwarder
    raise SystemExit(main())

