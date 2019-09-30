
def main() -> None:
    """Entrypoint to the ``celery`` umbrella command."""
    from chromium_kiosk.bin.chromium_kiosk import main as _main
    _main()


if __name__ == '__main__':  # pragma: no cover
    main()
