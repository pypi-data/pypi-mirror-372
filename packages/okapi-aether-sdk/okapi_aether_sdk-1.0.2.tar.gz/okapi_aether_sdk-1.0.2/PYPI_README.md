# Python SDK for OKAPI:Aether

This is a lightweight Python SDK to access the public OKAPI:Aether API.

## Installation

The SDK is easy to install using `pip`. We recommend creating a virtual environment for the project.

```
python3 -m venv .venv
source .venv/bin/activate
pip install okapi-aether-sdk
```

## Configuration
Authentication to OKAPI:Aether is performed via the following ENV variables (they can be set directly or via an `.env` file):
* `AETHER_AUTH0_USERNAME`
* `AETHER_AUTH0_PASSWORD`

The use of the env variables can be overriden by directly passing the appropriate username and password to the `login` method.

## Functionality

It allows for easy access to CDMs, fleet management, upload of ephemerides and maneuver plans, etc.

For more details, please consult the respective section in the OKAPI:Aether user manual.

### CLI
The okapi-aether-sdk comes with a command line interface. See the help command for additional usage information.

```
aether-api --help
```
