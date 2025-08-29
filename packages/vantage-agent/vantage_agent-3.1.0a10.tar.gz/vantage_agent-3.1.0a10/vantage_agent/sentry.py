"""Core module for Sentry related operations.

Copied from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/jobbergate_agent/utils/sentry.py.
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.utils import BadDsn

from vantage_agent.logger import logger
from vantage_agent.settings import SETTINGS


def init_sentry():
    """Initialize the Sentry SDK."""
    try:
        sentry_logging = LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR)

        sentry_sdk.init(
            dsn=SETTINGS.SENTRY_DSN,
            integrations=[sentry_logging],
            sample_rate=SETTINGS.SENTRY_SAMPLE_RATE,
            profiles_sample_rate=SETTINGS.SENTRY_PROFILING_SAMPLE_RATE,
            traces_sample_rate=SETTINGS.SENTRY_TRACES_SAMPLE_RATE,
            environment=SETTINGS.SENTRY_ENV,
        )

        logger.debug("Enabled Sentry since a valid DSN key was provided.")
    except BadDsn as e:
        logger.debug(f"Sentry could not be enabled: {e}")
