
def main():
    """Entrypoint to the ``celery`` umbrella command."""
    from granad_kiosk.bin.granad_kiosk import main as _main
    _main()


if __name__ == '__main__':  # pragma: no cover
    main()
