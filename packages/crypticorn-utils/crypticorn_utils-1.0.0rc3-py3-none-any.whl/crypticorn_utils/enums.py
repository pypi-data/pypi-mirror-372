"""Defines common enumerations used throughout the codebase for type safety and consistency."""

from enum import StrEnum as _StrEnum

class ApiEnv(_StrEnum):
    """The environment the API is being used with."""

    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    DOCKER = "docker"


class BaseUrl(_StrEnum):
    """The base URL to connect to the API."""

    PROD = "https://api.crypticorn.com"
    DEV = "https://api.crypticorn.dev"
    LOCAL = "http://localhost"
    DOCKER = "http://host.docker.internal"

    @classmethod
    def from_env(cls, env: ApiEnv) -> "BaseUrl":
        """Load the base URL from the API environment."""
        if env == ApiEnv.PROD:
            return cls.PROD
        elif env == ApiEnv.DEV:
            return cls.DEV
        elif env == ApiEnv.LOCAL:
            return cls.LOCAL
        elif env == ApiEnv.DOCKER:
            return cls.DOCKER
