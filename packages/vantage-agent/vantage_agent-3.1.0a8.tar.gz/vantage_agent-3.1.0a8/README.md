# Vantage Agent

## Install the package

To install the package from Pypi simply run `pip install vantage-agent`.

## Setup parameters

1. Setup dependencies

    Dependencies and environment are managed in the project by [Poetry](https://python-poetry.org/). To initiate the development environment run:

    ```bash
    make install
    ```

2. Setup `.env` parameters

    ```bash
    VANTAGE_AGENT_BASE_API_URL="<base-api-url>"
    VANTAGE_AGENT_OIDC_DOMAIN="<OIDC-domain>"
    VANTAGE_AGENT_OIDC_CLIENT_ID="<OIDC-audience>"
    VANTAGE_AGENT_OIDC_CLIENT_SECRET="<OIDC-app-client-id>"
    VANTAGE_AGENT_OIDC_USE_HTTPS="<OIDC-app-client-secret>"
    ```

## Local usage example

1. Run app

    ```bash
    vtg-run
    ```

    **Note**: this command assumes you're inside a virtual environment in which the package is installed.
