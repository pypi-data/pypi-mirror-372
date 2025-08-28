"""Provide to the agent the ability to load custom plugins that are installed on the same environment."""

from importlib.metadata import entry_points
from typing import Any, Dict

from buzz import handle_errors

from vantage_agent.logger import logger, logger_wraps


@logger_wraps()
def load_plugins(plugin_name: str) -> Dict[str, Any]:
    """Discover and load plugins available to the agent, allowing for third party ones to be included.

    Notice the ones shipped with the agent are also declared on the ``pyproject.toml`` file
    as plugins, even though they could be easily loaded directly from source. This aims
    to support tests and to demonstrate how to use the plugin system.

    Reference:
        https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
    """
    discovered_plugins = entry_points(group=f"vantage_agent.{plugin_name}")
    logger.info(f"Loaded plugins {discovered_plugins}")
    result = {}
    for plugin in discovered_plugins:
        with handle_errors(
            f"Failed to load plugin {plugin_name} from {plugin.value}",
            raise_exc_class=RuntimeError,
        ):
            content = plugin.load()

        result[plugin.name.lower()] = content

    logger.info("Discovered the following plugins for {}: {}", plugin_name, ", ".join(result.keys()))
    return result
