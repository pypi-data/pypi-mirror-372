import inspect
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Literal

import click
from dotenv import load_dotenv

from okapi_aether_sdk.aether_api import AetherApi
from okapi_aether_sdk.aether_satellites_api import AetherSatellitesApi
from okapi_aether_sdk.aether_sensors_api import AetherSensorsApi
from okapi_aether_sdk.aether_services_api import AetherServicesApi

# Aether API client classes
from okapi_aether_sdk.utils import get_default_logger, split_url_parts

logger = get_default_logger()

UUID_REGEX = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
    re.IGNORECASE,
)
API_CLASSES = {
    "satellites": AetherSatellitesApi,
    "sensors": AetherSensorsApi,
    "services": AetherServicesApi,
}


@click.group()
@click.option(
    "--env-file",
    "-e",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a .env file with API credentials.",
)
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging.")
@click.pass_context
def cli(ctx: click.Context, env_file: Path, verbose: bool):
    """Aether CLI: interact with Satellites, Sensors, and Services APIs."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose

    if env_file:
        load_dotenv(env_file)

    if verbose:
        logger.setLevel(logging.DEBUG)


@cli.command("run")
@click.option(
    "--module",
    "-m",
    type=click.Choice(list(API_CLASSES.keys()), case_sensitive=False),
    required=True,
    help="Which API module to use.",
)
@click.option(
    "--action",
    "-a",
    "operation",
    required=True,
    help="Name of the method to call on that module (e.g. get_satellite, predict_passes).",
)
@click.option(
    "--file",
    "-f",
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to a JSON file containing request body data (used for POST, PUT, or PATCH operations).",
)
@click.option(
    "--param",
    "-p",
    "params",
    multiple=True,
    metavar="KEY=VALUE",
    help="Inline key-value args; repeatable.",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Full path to the output file. If not provided, a default filename will be used.",
)
def run(module: str, operation: str, input_file: Path, params: tuple[str, ...], output_path: Path):
    """Run any command from the high level interface

    Run any of the available commands from the high level interfaces

    \f
    :param str module: API module containing the command
    :param str operation: Command to be executed
    :param Path input_file: Path to the input file needed for the command
    :param tuple[str, ...] params: Params of the command
    :param Path output_path: Path to the output file, if nedeed.
    """
    # Retrieve the API client class and instantiate it
    api_cls = API_CLASSES.get(module.lower())
    if not api_cls:
        raise click.BadParameter(f"Unsupported module: {module}")

    api_instance = api_cls()
    try:
        api_instance.login()
    except Exception as e:
        raise click.ClickException(f"Failed to login to {module} API: {e}")

    # Load JSON file (if provided)
    file_data = None
    if input_file:
        with input_file.open("r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
            except json.JSONDecodeError as e:
                raise click.UsageError(f"Invalid JSON in --file: {e}")

    # Parse key=value parameters
    kwargs: Dict[str, Any] = {}
    for kv in params:
        if "=" not in kv:
            raise click.BadParameter(f"Invalid param: {kv!r}. Use KEY=VALUE format.")
        key, val = kv.split("=", 1)
        try:
            parsed = json.loads(val)
        except json.JSONDecodeError:
            parsed = val

        kwargs[key] = parsed

    # Locate and validate the method
    if not hasattr(api_instance, operation):
        raise click.BadParameter(f"Module '{module}' has no method '{operation}'")
    method = getattr(api_instance, operation)
    sig = inspect.signature(method)
    accepted_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

    # Call the method
    try:
        logger.info("Calling %s on module %s", operation, module)
        if file_data is not None:
            result = method(file_data, **accepted_kwargs)
        else:
            result = method(**accepted_kwargs)
    except Exception as e:
        raise click.ClickException(f"API method call failed: {e}")

    # Handle UUID result (request_id)
    if isinstance(result, str) and UUID_REGEX.match(result):
        logger.info(
            f"Request submitted via '{operation}'. "
            f"To retrieve results, use 'get_{operation}_results' with --param request_id={result}."
        )
        return

    # Prepare output path for HTML or JSON
    if not output_path:
        file_extension = (
            "html" if operation == "get_od_residuals_plot" and isinstance(result, str) else "json"
        )
        output_path = Path(f"api_call_{module}__{operation}.{file_extension}")
    else:
        file_extension = output_path.suffix.lstrip(".").lower()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if file_extension == "html":
            output_path.write_text(result, encoding="utf-8")
        else:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
    except Exception as e:
        raise click.FileError(
            str(output_path), hint=f"Could not write {file_extension.upper()} output: {e}"
        )

    logger.info(f"✓ Saved result to {output_path}")


@cli.command("get-request")
@click.option(
    "--url",
    "-u",
    required=True,
    help="Full or relative API URL (e.g. 'https://.../oems/...' or just 'oems/...').",
)
@click.option(
    "--response-format",
    "-f",
    type=click.Choice(["json", "html"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Format for saving the response output. Can be 'json' or 'html'.",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Full path to the output file. If not provided, a default filename will be used.",
)
def get_request(url: str, response_format: Literal["json", "html"], output_path: Path):
    """Execute a GET request to the given endpoint

    Perform a raw GET request to the specified API endpoint and
    save the JSON response to a file named after the endpoint.

    \f
    :param str url: Full or relative endpoint
    :param str response_format: Default format of the response. Defaults to json.
    :param Path output_path: Path where to save the obtained response
    """

    # Determine base URL vs. relative endpoint
    if url.lower().startswith("http"):
        base_url, endpoint = split_url_parts(url)
        api = AetherApi(base_url)
    else:
        endpoint, api = url, AetherApi()

    try:
        api.login()
    except Exception as e:
        raise click.ClickException(f"Failed to login to API: {e}")

    logger.info("GET %s", endpoint)
    try:
        result = api.get(endpoint, response_format)
    except Exception as e:
        raise click.ClickException(f"API request failed: {e}")

    # Prepare output path for HTML or JSON
    if not output_path:
        safe = endpoint.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("=", "_")
        extension = ".html" if response_format.lower() == "html" else ".json"
        output_path = Path(f"api_call_{safe}{extension}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if response_format == "html":
            output_path.write_text(result, encoding="utf-8")
        else:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
    except Exception as e:
        raise click.FileError(
            str(output_path), hint=f"Could not write {response_format.upper()} output: {e}"
        )

    logger.info(f"✓ Saved result to {output_path}")


@cli.command("send-request")
@click.option(
    "--url",
    "-u",
    required=True,
    help="Full or relative API URL (e.g. 'https://.../requests' or just '.../requests'",
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["POST", "PUT", "PATCH"], case_sensitive=False),
    default="POST",
    show_default=True,
)
@click.option(
    "--file",
    "-f",
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to a JSON file containing request body data (used for POST, PUT, or PATCH operations).",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Full path to the output file. If not provided, a default filename will be used.",
)
def send_request(url: str, method: str, input_file: Path, output_path: Path):
    """Execute a POST/PUT/PATCH request to the given endpoint

    Send a POST/PUT/PATCH request to the specified API endpoint with a JSON payload,
    then save the JSON response or log a request_id if returned.

    \f
    :param str url: Full or relative endpoint
    :param str method: Method to be executed {POST, PUT, PATCH}. Defaults to Post.
    :param Path input_file: Json formatted input file to be used as payload
    :param Path output_path: Path where to save the obtained response
    """
    # Determine base URL vs. relative endpoint
    if url.lower().startswith("http"):
        base_url, endpoint = split_url_parts(url)
        api = AetherApi(base_url)
    else:
        endpoint, api = url, AetherApi()

    try:
        api.login()
    except Exception as e:
        raise click.ClickException(f"Failed to login to API: {e}")

    # Load JSON payload if provided
    payload: Dict[str, Any] = {}
    if input_file:
        try:
            payload = json.loads(input_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise click.UsageError(f"Invalid JSON in --file: {e}")

    # Send request
    logger.info("%s %s", method.upper(), endpoint)
    method = method.upper()
    if method == "POST":
        result = api.post(endpoint, payload)
    elif method == "PUT":
        result = api.put(endpoint, payload)
    elif method == "PATCH":
        result = api.patch(endpoint, payload)
    else:
        raise click.BadParameter(f"Unsupported method: {method}")

    # If result is a request_id, log instructions and exit
    if isinstance(result, dict) and (request_id := result.get("request_id")):
        logger.info(
            f"Request to '{endpoint}' returned request_id={request_id}. "
            f"To fetch results, run:\n"
            f"  aether-cli get-request --url '{endpoint}/results/{request_id}'"
        )
        return

    # Save JSON response
    if not output_path:
        safe = endpoint.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("=", "_")
        output_path = Path(f"api_call_{safe}.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Write JSON in one go
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
    except Exception as e:
        raise click.FileError(str(output_path), hint=f"Could not write JSON output: {e}")

    logger.info(f"✓ Saved result to {output_path}")
