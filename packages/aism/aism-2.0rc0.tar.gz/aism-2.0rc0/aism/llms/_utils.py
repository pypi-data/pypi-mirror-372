import os
from typing import Optional

try:
    import dotenv  # pip install python-dotenv
except ModuleNotFoundError:
    dotenv = None

if dotenv is not None:
    dotenv.load_dotenv()


def getenv(key: str, /) -> Optional[str]:
    return os.environ.get(key, None)


def try_getenv(key: str, /) -> str:
    s = getenv(key)
    if s is None:
        raise OSError(
            f"Could not found environment variable: {key!r}"
            + (
                "\nif you're using .env files, install `python-dotenv`"
                if dotenv is None
                else ", and is not found in loaded .env files"
            )
        )

    return s


def safe_base_url(base: str) -> str:
    return base.rstrip("/")
