"""Core module for defining operations related to the squeue command."""

import asyncio
import subprocess

from jsondiff import diff
from loguru import logger

from vantage_agent.helpers import (
    cache_dict,
    load_cached_dict,
    parse_slurm_queue,
)
from vantage_agent.logicals.vantage_api import (
    upload_slurm_queue,
)
from vantage_agent.settings import SETTINGS


def upload_squeue_queue():
    """Upload Slurm's queues information to the Vantage API."""
    logger.debug("Getting Slurm's queue information")
    result = subprocess.run([SETTINGS.SQUEUE_PATH, "-o", "%all"], stdout=subprocess.PIPE, text=True)  # noqa
    output = result.stdout

    logger.debug("Parsing Slurm's queue")
    current_config = parse_slurm_queue(output)

    logger.debug("Loading cached Slurm's queue")
    cached_config = load_cached_dict("slurm_queue.json")

    logger.debug("Computing difference between cached and current queue")
    diff_queue = diff(cached_config, current_config, marshal=True)

    if diff_queue:
        logger.debug("Detected changes in Slurm's configuration. Uploading to the API...")
        asyncio.run(upload_slurm_queue(diff_queue))
        cache_dict(current_config, "slurm_queue.json")
    else:
        logger.debug("No changes detected in Slurm's queue.")
