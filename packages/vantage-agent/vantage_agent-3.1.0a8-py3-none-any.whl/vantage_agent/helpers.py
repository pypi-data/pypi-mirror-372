"""Core module for utility functions for the project."""

import json
from typing import Any

from vantage_agent.settings import SETTINGS


def cache_dict(input_dict: dict[Any, Any], file_name: str) -> None:
    """Cache the input dict at SETTINGS.CACHE_DIR/filename."""
    if not file_name.endswith(".json"):
        file_name += ".json"

    with open(f"{SETTINGS.CACHE_DIR}/{file_name}", "w") as f:
        json.dump(input_dict, f)


def load_cached_dict(file_name: str) -> dict[Any, Any]:
    """Load the cached dict from SETTINGS.CACHE_DIR/filename."""
    if not file_name.endswith(".json"):
        file_name += ".json"

    try:
        with open(f"{SETTINGS.CACHE_DIR}/{file_name}", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def parse_slurm_config(output: str) -> dict[str, str]:
    """Parse the output of `scontrol show config` and return a dictionary."""
    config_dict = {}

    for line in output.splitlines():
        if line.strip() and "Configuration data as of" not in line:
            if "=" in line:
                key, value = line.split("=", 1)
                config_dict[key.strip()] = value.strip()

    return config_dict


def parse_slurm_partitions(output: str) -> dict[str, dict[str, str]]:
    """Parse the output of `scontrol show partition` and return a dictionary."""
    partitions: dict[str, dict[str, str]] = {}
    partition_dict: dict[str, str] = {}
    current_partition_name = ""

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("PartitionName="):
            if current_partition_name:
                partitions[current_partition_name] = partition_dict
            current_partition_name = line.split("=")[1]
            partition_dict = {}

        key_value_pairs = line.split()
        for pair in key_value_pairs:
            if "=" in pair and current_partition_name not in pair:  # ignore the partition name key-value pair
                key, value = pair.split("=", 1)
                partition_dict[key.strip()] = value.strip()

    if current_partition_name:  # save the last partition data
        partitions[current_partition_name] = partition_dict

    return partitions


def parse_slurm_nodes(output: str) -> dict[str, dict[str, str]]:
    """Parse the output of `scontrol show nodes` and return a list of dictionaries."""
    nodes_dict = {}
    node_dict: dict[str, str] = {}

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("NodeName="):
            if node_dict:
                nodes_dict[node_dict["NodeName"]] = {k: v for k, v in node_dict.items() if k != "NodeName"}
                node_dict = {}
            node_name = line.split("=")[1]
            node_dict["NodeName"] = node_name
        elif line.startswith("OS"):
            key, value = line.split("=", 1)
            node_dict[key.strip()] = value.strip()
            continue
        elif line.startswith("Reason"):
            key, value = line.split("=", 1)
            node_dict[key.strip()] = value.strip()
            continue

        key_value_pairs = line.split()
        for pair in key_value_pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                node_dict[key.strip()] = value.strip()

    # add the last element to the dictionary
    if node_dict:
        nodes_dict[node_dict["NodeName"]] = {k: v for k, v in node_dict.items() if k != "NodeName"}

    return nodes_dict


def parse_slurm_queue(output: str) -> list[dict[str, str]]:
    """Parse the output of `squeue -o %all` and return a list of dictionaries.

    Each dict represent one job with field names from the header.
    """
    lines = output.strip().splitlines()
    if not lines or len(lines) < 2:
        return {}

    # First line: headers
    headers = [h.strip().lower().replace(" ", "_") for h in lines[0].split("|")]
    result = {}
    for line in lines[1:]:
        values = line.strip().split("|")
        # Fix lines with less columns then the header
        if len(values) < len(headers):
            values += [""] * (len(headers) - len(values))
        elif len(values) > len(headers):
            values = values[: len(headers)]

        job = dict(zip(headers, values))
        identifier = f"{job['jobid']}-{job['name']}"
        result[identifier] = job

    return result
