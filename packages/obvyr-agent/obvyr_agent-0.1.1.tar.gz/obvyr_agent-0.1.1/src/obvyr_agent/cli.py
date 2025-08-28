import logging
import time
from typing import List

import click

from obvyr_agent.api_client import ObvyrAPIClient
from obvyr_agent.command_wrapper import run_command
from obvyr_agent.config import AgentSettings, Settings, get_settings
from obvyr_agent.schemas import RunCommandResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================================
# CLI Support Functions
# ===================================


def list_available_agents(settings: Settings) -> None:
    """
    Lists all available agents.
    """
    agents = settings.list_agents()

    if len(agents) == 0:
        click.echo("\nNo agents available.\n")
        return

    click.echo("\nAvailable agents:\n")
    for agent in agents:
        click.echo(f"  - {agent}")
    click.echo("")


def show_agent_config(settings: Settings) -> None:
    """
    Shows the configuration for the active agent.
    """
    config = settings.show_config()

    click.echo("\nActive agent configuration:\n")
    for key, value in config.items():
        click.echo(f"  {key}: {value}")
    click.echo("")


def has_handled_initial_options(
    command: List[str], list_agents: bool, show_config: bool, settings: Settings
) -> bool:
    """Handle initial options for listing agents or showing configuration."""
    if command:
        return False

    if list_agents:
        list_available_agents(settings)
        return True

    if show_config:
        show_agent_config(settings)
        return True

    raise click.UsageError(
        "\n".join(
            (
                "No command provided.",
                "Usage: obvyr-agent <command> [arguments]",
                "Try 'obvyr-agent --help' for more information.",
            )
        )
    )


def fetch_active_agent(settings: Settings) -> AgentSettings:
    """Retrieve the active agent from settings."""
    active_agent = settings.get_agent()
    logger.info(f"Using agent: {settings.ACTIVE_AGENT}")
    return active_agent


def display_output(response: RunCommandResponse) -> None:
    """Display the command's output and errors."""
    if response.stdout:
        click.echo(f"\n{response.stdout}")

    if response.stderr:
        click.echo(f"\n{response.stderr}", err=True)

    output = (
        f"\nExecuted by {click.style(response.user, fg='green')} "
        f"in {click.style(f'{response.execution_time:.2f}s', fg='blue')}\n"
    )
    click.echo(output)


def send_to_api(settings: Settings, data: RunCommandResponse) -> None:
    """
    Sends execution data to the Obvyr API.

    :param data: Command execution result to be sent to the API.
    """
    active_agent = settings.get_agent()

    if not active_agent.API_KEY:
        logger.warning("API submission disabled: No API key configured.")
        return

    try:
        with ObvyrAPIClient(
            api_key=active_agent.API_KEY,
            base_url=active_agent.API_URL,
            timeout=active_agent.TIMEOUT,
            verify_ssl=active_agent.VERIFY_SSL,
        ) as client:
            start_time = time.time()
            response = client.send_data("/collect", data.as_form_payload())
            end_time = time.time()

            logger.info(f"API request time: {end_time - start_time:.2f}s")

            if response:
                logger.info(f"Successfully sent data to API: {response}")
            else:
                logger.warning("Failed to send data to API.")

    except Exception as e:
        logger.error(f"API request failed: {e}")


# ===================================
# Click CLI
# ===================================


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1, required=False, type=click.UNPROCESSED)
@click.option(
    "--list-agents",
    "list_agents",
    is_flag=True,
    help="List all available agents.",
)
@click.option(
    "--show-config",
    "show_config",
    is_flag=True,
    help="Show config for active agent.",
)
def cli_run_process(
    command: List[str], list_agents: bool, show_config: bool
) -> None:
    """
    Executes a system command while using the Obvyr agent configuration.
    """
    try:
        settings = get_settings()

        if has_handled_initial_options(
            command, list_agents, show_config, settings
        ):
            return

        active_agent = fetch_active_agent(settings)

        response: RunCommandResponse = run_command(list(command))

        if active_agent.API_URL and active_agent.API_KEY:
            send_to_api(settings, response)

        display_output(response)

        if response.returncode != 0:
            raise click.exceptions.Exit(response.returncode)

    except Exception as e:
        raise click.ClickException(str(e)) from e
