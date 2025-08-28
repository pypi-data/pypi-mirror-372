"""Core module for defining operations related to calling the Vantage API."""

from textwrap import dedent
from typing import Any, TypedDict

from loguru import logger

from vantage_agent.settings import SETTINGS
from vantage_agent.vantage_api_client import AsyncBackendClient


class UploadSlurmConfigSuccess(TypedDict):
    """Type definition for the success response of the uploadSlurmConfig mutation."""

    data: dict[Any, Any]
    errors: list[Any] | None


async def upload_slurm_config(slurm_config: dict[Any, Any]) -> None:
    """Upload Slurm's configuration to the Vantage API."""
    query = dedent(
        """
        mutation($config: JSONScalar!, $clientId: String!) {
            uploadSlurmConfig(config: $config, clientId: $clientId) {
                ... on UploadSlurmConfigSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"config": slurm_config, "clientId": SETTINGS.OIDC_CLIENT_ID}}
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while uploading Slurm's configurations: {response_data}")


async def upload_slurm_partitions(slurm_partitions: dict[Any, Any]) -> None:
    """Upload Slurm's partitions information to the Vantage API."""
    query = dedent(
        """
        mutation($partitions: JSONScalar!, $clientId: String!) {
            uploadSlurmPartitions(partitions: $partitions, clientId: $clientId) {
                ... on UploadSlurmPartitionsSuccess {
                    message
                }
            }
        }
        """
    )
    body = {
        "query": query,
        "variables": {"partitions": slurm_partitions, "clientId": SETTINGS.OIDC_CLIENT_ID},
    }
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while uploading partitions: {response_data}")


async def upload_slurm_nodes(slurm_nodes: dict[Any, Any]) -> None:
    """Upload Slurm's nodes information to the Vantage API."""
    query = dedent(
        """
        mutation($nodes: JSONScalar!, $clientId: String!) {
            uploadSlurmNodes(nodes: $nodes, clientId: $clientId) {
                ... on UploadSlurmNodesSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"nodes": slurm_nodes, "clientId": SETTINGS.OIDC_CLIENT_ID}}
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while uploading nodes: {response_data}")


async def clean_slurm_partitions(slurm_partitions: list[str] | set[str]) -> None:
    """Clean up partitions that are no longer present in Slurm."""
    query = dedent(
        """
        mutation($partitions: [String!]!, $clientId: String!) {
            cleanSlurmPartitions(partitions: $partitions, clientId: $clientId) {
                ... on CleanSlurmPartitionsSuccess {
                    message
                }
            }
        }
        """
    )
    body = {
        "query": query,
        "variables": {"partitions": slurm_partitions, "clientId": SETTINGS.OIDC_CLIENT_ID},
    }
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while cleaning partitions: {response_data}")


async def clean_slurm_nodes(slurm_nodes: list[str] | set[str]) -> None:
    """Clean up nodes that are no longer present in Slurm."""
    query = dedent(
        """
        mutation($nodes: [String!]!, $clientId: String!) {
            cleanSlurmNodes(nodes: $nodes, clientId: $clientId) {
                ... on CleanSlurmNodesSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"nodes": slurm_nodes, "clientId": SETTINGS.OIDC_CLIENT_ID}}
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while cleaning nodes: {response_data}")


async def upload_slurm_queue(slurm_queue: dict[Any, Any]) -> None:
    """Upload Slurm's queue information to the Vantage API."""
    query = dedent(
        """
        mutation($queue: JSONScalar!, $clientId: String!) {
            uploadSlurmQueue(queue: $queue, clientId: $clientId) {
                ... on UploadSlurmQueueSuccess {
                    message
                }
            }
        }
        """
    )
    body = {
        "query": query,
        "variables": {"queue": slurm_queue, "clientId": SETTINGS.OIDC_CLIENT_ID},
    }
    async with AsyncBackendClient() as backend_client:
        res = await backend_client.post("/cluster/graphql", json=body)

    response_data: UploadSlurmConfigSuccess = res.json()
    logger.debug(f"Response from Vantage API while uploading queue: {response_data}")
