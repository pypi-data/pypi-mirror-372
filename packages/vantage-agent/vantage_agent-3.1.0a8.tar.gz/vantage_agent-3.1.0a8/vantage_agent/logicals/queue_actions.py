"""Core module for defining operations related to cluster queue actions."""

import asyncio
import subprocess
from string import Template
from textwrap import dedent
from typing import Any, TypedDict

from loguru import logger

from vantage_agent.exceptions import VantageApiError
from vantage_agent.logger import log_error
from vantage_agent.settings import SETTINGS
from vantage_agent.vantage_api_client import AsyncBackendClient


class QueueActionResponse(TypedDict):
    """Type definition for the queue action response."""

    data: dict[Any, Any]
    errors: list[Any] | None


async def fetch_cluster_queue_actions() -> list[dict[str, Any]]:
    """Fetch all cluster queue actions for the current cluster."""
    logger.debug("Fetching cluster queue actions from Vantage API")

    query = dedent(
        Template(
            """
        query clusterQueueActions {
            clusterQueueActions(
                first: 100
                filters: {
                    clusterName: {
                        eq: "$clusterName"
                    }
                }
            ) {
                edges {
                    node {
                        id
                        clusterName
                        queueId
                        action
                        queue {
                            id
                            name
                            info
                        }
                    }
                }
                total
            }
        }
        """
        ).substitute(clusterName=SETTINGS.CLUSTER_NAME)
    )

    body = {"query": query}

    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: QueueActionResponse = res.json()

    if response_data.get("errors"):
        logger.error(f"Error fetching cluster queue actions: {response_data['errors']}")
        return []

    cluster_actions = response_data.get("data", {}).get("clusterQueueActions", {}).get("edges", [])
    logger.debug(f"Found {len(cluster_actions)} queue actions for cluster {SETTINGS.CLUSTER_NAME}")
    return cluster_actions


async def remove_queue_action(action_id: int) -> bool:
    """Remove a queue action from the database."""
    logger.debug(f"Removing queue action with ID: {action_id}")

    query = dedent(
        """
        mutation removeQueueAction($id: Int!) {
            removeQueueAction(id: $id) {
                __typename
                ... on RemoveQueueActionSuccess {
                    message
                }
                ... on InvalidInput {
                    message
                }
            }
        }
        """
    )

    body = {"query": query, "variables": {"id": action_id}}

    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: QueueActionResponse = res.json()

    if response_data.get("errors"):
        logger.error(f"Error removing queue action {action_id}: {response_data['errors']}")
        return False

    result = response_data.get("data", {}).get("removeQueueAction", {})
    if result.get("__typename") == "RemoveQueueActionSuccess":
        logger.debug(f"Successfully removed queue action {action_id}")
        return True
    elif result.get("__typename") == "InvalidInput":
        logger.warning(f"Queue action {action_id} not found: {result.get('message')}")
        return True  # Consider it successful since the action is already gone
    else:
        logger.error(f"Unexpected response when removing queue action {action_id}: {result}")
        return False


def execute_scancel(job_id: str) -> bool:
    """Execute scancel command for a specific job ID."""
    logger.debug(f"Executing scancel for job ID: {job_id}")

    try:
        result = subprocess.run(
            [SETTINGS.SCANCEL_PATH, job_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )

        if result.returncode == 0:
            logger.info(f"Successfully cancelled job {job_id}")
            return True
        else:
            stderr_output = result.stderr.lower()
            if "invalid job id" in stderr_output or "no such job" in stderr_output:
                logger.warning(f"Job {job_id} does not exist or was already cancelled")
                return True
            else:
                logger.error(f"Failed to cancel job {job_id}: {result.stderr}")
                return False

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while trying to cancel job {job_id}")
        return False
    except Exception as e:
        logger.error(f"Exception while trying to cancel job {job_id}: {e}")
        return False


def extract_job_id_from_queue_info(queue_info: dict[str, Any]) -> str | None:
    """Extract job ID from queue info dictionary."""
    if not queue_info:
        return None

    if isinstance(queue_info, dict):
        if "jobid" in queue_info:
            return str(queue_info["jobid"])
        else:
            logger.warning(f"Could not extract job ID from queue info: {queue_info}")
            return None


def process_cluster_queue_actions():
    """Process all cluster queue actions - cancel jobs and clean up actions."""
    logger.debug("Processing cluster queue actions")

    with VantageApiError.handle_errors("Failed to process cluster queue actions", do_except=log_error):
        asyncio.run(_process_cluster_queue_actions_async())


async def _process_cluster_queue_actions_async():
    """Async implementation of process_cluster_queue_actions."""
    actions = await fetch_cluster_queue_actions()

    if not actions:
        logger.debug("No queue actions to process")
        return

    for action in actions:
        action_id = action["node"]["id"]
        queue_info = action["node"].get("queue", {}).get("info", {})
        action_type = action["node"]["action"]

        logger.debug(f"Processing action {action_id} of type {action_type}")

        if action_type.lower() != "cancel":
            logger.warning(f"Unsupported action type: {action_type}")
            continue

        job_id = extract_job_id_from_queue_info(queue_info)

        if job_id is None:
            logger.error(f"Could not extract job ID for action {action_id}, removing action")
            await remove_queue_action(action_id)
            continue

        success = execute_scancel(job_id)

        if success:
            logger.info(f"Successfully cancelled job {job_id} for action {action_id}")
        else:
            logger.error(f"Failed to cancel job {job_id} for action {action_id}")
