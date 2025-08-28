"""Core module for agent health related operations.

Copied and adjusted from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/jobbergate_agent/jobbergate/report_health.py.
"""

from textwrap import dedent

from loguru import logger

from vantage_agent.exceptions import VantageApiError
from vantage_agent.logger import log_error
from vantage_agent.settings import SETTINGS
from vantage_agent.vantage_api_client import AsyncBackendClient


async def report_health_status() -> None:
    """Ping the API to report the agent's status."""
    logger.debug("Reporting status to the API")
    with VantageApiError.handle_errors("Failed to report agent status", do_except=log_error):
        query = dedent(
            """\
            mutation ($clientId: String!, $interval: Int!) {
                reportAgentHealth(clientId: $clientId, interval: $interval)
            }"""
        )
        body = {
            "query": query,
            "variables": {
                "clientId": SETTINGS.OIDC_CLIENT_ID,
                "interval": SETTINGS.TASK_JOBS_INTERVAL_SECONDS,
            },
        }
        async with AsyncBackendClient() as backend_client:
            response = await backend_client.post("cluster/graphql", json=body)
        response.raise_for_status()
