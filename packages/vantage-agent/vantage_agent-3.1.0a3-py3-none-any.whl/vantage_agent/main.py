"""Main module of the project for starting the agent."""

import asyncio

from loguru import logger

from vantage_agent.scheduler import init_scheduler, shut_down_scheduler
from vantage_agent.sentry import init_sentry


def main():
    """Start the agent by initiating the scheduler."""
    logger.info("Starting the Vantage Agent")
    init_sentry()
    scheduler = init_scheduler()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        logger.info("Shutting down the Vantage Agent")
        shut_down_scheduler(scheduler)  # pragma: no cover


if __name__ == "__main__":
    main()  # pragma: no cover
