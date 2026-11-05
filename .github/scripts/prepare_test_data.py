"""Stage the reviewed CMU dictionary for CI; never download it from a test."""

import argparse
import hashlib
import io
from pathlib import Path
import urllib.request
import zipfile

URL = (
    "https://raw.githubusercontent.com/nltk/nltk_data/"
    "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a/packages/corpora/cmudict.zip"
)
SIZE = 896069
SHA256 = "d07cca47fd72ad32ea9d8ad1219f85301eeaf4568f8b6b73747506a71fb5afd6"


def prepare(destination: Path, archive: Path | None = None) -> None:
    """Verify the exact reviewed archive before extracting into a new directory.

    ``archive`` permits an explicitly acquired local copy for offline validation.
    The dictionary and its license stay outside the checkout under runner.temp.
    """
    if archive is None:
        with urllib.request.urlopen(URL, timeout=60) as source:
            data = source.read(SIZE + 1)
    else:
        with archive.open("rb") as source:
            data = source.read(SIZE + 1)
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("CMU dictionary archive does not match the reviewed size/SHA-256")
    # Only these exact, reviewed bytes are ever extracted; occupied destinations
    # are refused so an earlier resource or unrelated data cannot be overwritten.
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        bundle.extractall(destination / "corpora")
    print(f"Prepared cmudict: {SIZE} bytes; SHA-256 {SHA256}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--archive", type=Path, help="Use an already acquired local archive")
    args = parser.parse_args()
    prepare(args.destination, args.archive)


if __name__ == "__main__":
    main()
