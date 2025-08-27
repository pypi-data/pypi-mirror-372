# This file is used to check if the crypticorn version is greater than 2.18
# This is to be compatible with this new utils library
# otherwise prometheus reqisters metrics twice, resulting in an exception

import importlib.metadata
from importlib.metadata import PackageNotFoundError

try:
    crypticorn_version = importlib.metadata.distribution("crypticorn").version
    parts = crypticorn_version.split(".")
    has_migrated = parts[0] >= "2" and parts[1] > "18"
except PackageNotFoundError:
    has_migrated = True
