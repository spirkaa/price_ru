import logging

from .app import main

if __name__ == "__main__":
    __version__ = "0.0.1"
    logging.basicConfig(
        format="%(asctime)s [%(levelname)8s] [%(name)s:%(lineno)s:%(funcName)20s()] --- %(message)s",  # noqa
        level=logging.INFO,
    )

    main()
