"""Core module for defining global settings of the Vantage Agent."""

import re
import sys
from pathlib import Path, PosixPath
from typing import Annotated, Optional

from pydantic import AnyHttpUrl, Field, confloat, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from vantage_agent.logger import logger


def _define_dotenv_file_location() -> PosixPath:
    """Define the location of the .env file based on the env var `DOTENV_FILE_LOCATION`.

    In case it is not set, the default location is defined as `.env`.
    """
    default_dotenv_file_location = Path("/var/snap/vantage-agent/common/.env")
    if default_dotenv_file_location.exists():
        return default_dotenv_file_location
    return Path(".env")


class Settings(BaseSettings):
    """Settings for the Vantage Agent."""

    PARTITIONS_JSON_PATH: Path = Path("/nfs/slurm/etc/aws/partitions.json")
    SCONTROL_PATH: Path = Path("/usr/bin/scontrol")
    SQUEUE_PATH: Path = Path("/usr/bin/squeue")
    SCANCEL_PATH: Path = Path("/usr/bin/scancel")
    SLURM_CONF_PATH: Path = Path("/etc/slurm/slurm.conf")
    GRES_CONF_PATH: Path = Path("/etc/slurm/gres.conf")

    IS_CLOUD_CLUSTER: bool = False

    # Vantage API info
    BASE_API_URL: Annotated[str, AnyHttpUrl] = "https://apis.vantagecompute.ai"

    # Sentry
    SENTRY_DSN: Optional[AnyHttpUrl] = None
    SENTRY_ENV: str = "local"
    SENTRY_TRACES_SAMPLE_RATE: Annotated[float, confloat(gt=0, le=1.0)] = 0.01
    SENTRY_SAMPLE_RATE: Annotated[float, confloat(gt=0.0, le=1.0)] = 0.25
    SENTRY_PROFILING_SAMPLE_RATE: Annotated[float, confloat(gt=0.0, le=1.0)] = 0.01

    # OIDC config for machine-to-machine security
    OIDC_DOMAIN: str
    OIDC_CLIENT_ID: str
    OIDC_CLIENT_SECRET: str
    OIDC_USE_HTTPS: bool = True
    CLUSTER_NAME: str

    CACHE_DIR: Path = Path.home() / ".cache/vantage-agent"

    # Task settings
    TASK_JOBS_INTERVAL_SECONDS: int = Field(30, ge=10, le=3600)  # seconds
    TASK_SELF_UPDATE_INTERVAL_SECONDS: Optional[int] = Field(None, ge=0)  # seconds

    @model_validator(mode="before")
    @classmethod
    def validade_cluster_name(cls, values):
        """Pre validator to set default values."""
        if not values.get("CLUSTER_NAME") and values.get("OIDC_CLIENT_ID"):
            client_regex = (
                r"^(.*)-([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"  # noqa
            )
            client_id_regex = re.compile(client_regex)
            match = client_id_regex.match(values.get("OIDC_CLIENT_ID"))
            if match is not None:
                cluster_name = match.group(1)
                values.update(
                    CLUSTER_NAME=cluster_name,
                )
        return values

    @field_validator("SCONTROL_PATH", mode="after")
    @classmethod
    def validate_scontrol_path(cls, v: Path) -> Path:
        """Ensure that the SCONTROL_PATH is an absolute path."""
        if not v.is_absolute():
            raise ValueError("SCONTROL_PATH must be an absolute path")
        return v

    model_config = SettingsConfigDict(
        env_prefix="VANTAGE_AGENT_", env_file=_define_dotenv_file_location(), extra="ignore"
    )


def _init_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except ValueError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = _init_settings()
