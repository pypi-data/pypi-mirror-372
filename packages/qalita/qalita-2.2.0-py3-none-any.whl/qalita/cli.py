"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import sys
import json
import base64
import yaml
import click

from qalita.internal.utils import logger, get_version


# Config to pass to the commands
class Config(object):

    def __init__(self):
        self.name = ""
        self.mode = ""
        self.token = ""
        self.url = ""
        self.verbose = False
        self.agent_id = None
        self.config = None
        self._qalita_home = os.path.expanduser("~/.qalita")
        # con = sqlite3.connect("agent.db")

    @property
    def qalita_home(self):
        if not self._qalita_home:
            self._qalita_home = os.environ.get(
                "QALITA_HOME", os.path.expanduser("~/.qalita")
            )
        return self._qalita_home

    def save_source_config(self):
        config_path = os.path.join(self._qalita_home, "qalita-conf.yaml")
        abs_path = os.path.abspath(config_path)

        # Ensure the directory exists before saving the file
        os.makedirs(self._qalita_home, exist_ok=True)

        logger.info(f"Saving source configuration to [{abs_path}]")
        with open(abs_path, "w") as file:
            yaml.dump(self.config, file)

    def load_source_config(self, verbose=True):
        config_path = os.path.join(self._qalita_home, "qalita-conf.yaml")
        abs_path = os.path.abspath(config_path)

        try:
            if verbose:
                logger.info(f"Loading source configuration from [{abs_path}]")
            with open(abs_path, "r") as file:
                self.config = yaml.safe_load(file)
                return self.config
        except FileNotFoundError:
            logger.warning(
                f"Configuration file [{abs_path}] not found, creating a new one."
            )
            self.config = {"version": 1, "sources": []}
            self.save_source_config()
            return self.config
        except Exception as e:
            logger.warning(
                f"An unexpected error occurred while loading the configuration [{abs_path}]: {e}"
            )
            self.config = {"version": 1, "sources": []}
            self.save_source_config()
            return self.config

    def get_agent_file_path(self):
        """Get the path for the agent file based on QALITA_HOME env or default."""
        return os.path.join(self._qalita_home, ".agent")

    def get_agent_run_path(self):
        """Get the path for the agent run folder based on QALITA_HOME env or default."""
        return os.path.join(self._qalita_home, "agent_run_temp")

    def save_agent_config(self, data):
        """Save the agent config in file to persist between context."""
        agent_file_path = self.get_agent_file_path()

        # Ensure the directory exists before saving the file
        os.makedirs(os.path.dirname(agent_file_path), exist_ok=True)

        with open(agent_file_path, "wb") as file:  # open in binary mode
            json_str = json.dumps(data, indent=4)  # convert to json string
            json_bytes = json_str.encode("utf-8")  # convert to bytes
            base64_bytes = base64.b64encode(json_bytes)  # encode to base64
            file.write(base64_bytes)

    def load_agent_config(self):
        agent_file_path = self.get_agent_file_path()
        try:
            with open(agent_file_path, "rb") as file:  # open in binary mode
                base64_bytes = file.read()  # read base64
                json_bytes = base64.b64decode(base64_bytes)  # decode from base64
                json_str = json_bytes.decode("utf-8")  # convert to string
                return json.loads(json_str)  # parse json
        except FileNotFoundError as exception:
            logger.error(f"Agent can't load data file : {exception}")
            logger.error("Make sure you have logged in before > qalita agent login")
            sys.exit(1)

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id

    def json(self):
        data = {
            "name": self.name,
            "mode": self.mode,
            "token": self.token,
            "url": self.url,
            "verbose": self.verbose,
        }
        return data


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@click.option(
    "--ui",
    is_flag=True,
    default=os.environ.get("QALITA_AGENT_UI", False),
    help="Open the local web UI dashboard",
)
@click.option(
    "--port",
    default=os.environ.get("QALITA_AGENT_UI_PORT", 7070),
    show_default=True,
    type=int,
    help="Port for the local web UI",
)
@click.option(
    "--host",
    default=os.environ.get("QALITA_AGENT_UI_HOST", "localhost"),
    show_default=True,
    help="Host interface to bind the local web UI",
)
@click.pass_context
def cli(ctx, ui=False, port=7070, host="localhost"):
    """
    ------------------ Qalita Platform Command Line Interface ------------------\n\r
    Hello and thanks for using Qalita Platform to monitor and ensure the quality of your data. \n\r
    ----------------------------------------------------------------------------\n\r
    Please, Help us improve our service by reporting any bug by filing a bug report, Thanks ! \n\r
    mail : contact@qalita.io \n\r
    ----------------------------------------------------------------------------"""
    if ui:
        try:
            from qalita.web.app import run_dashboard_ui
        except Exception as exc:
            logger.error(f"Unable to start web UI: {exc}")
        else:
            # Instantiate a Config to pass into the UI
            cfg = Config()
            cfg.load_source_config(verbose=False)
            run_dashboard_ui(cfg, host=host, port=port)
        raise SystemExit(0)
    # If invoked without a subcommand and without --ui, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        raise SystemExit(0)


@cli.command(context_settings=dict(help_option_names=["-h", "--help"]))
def version():
    """
    Display the version of the cli
    """
    print("--- QALITA CLI Version ---")
    print(f"Version : {get_version()}")


def add_commands_to_cli():
    from qalita.commands import agent, source, pack

    # Add pack command group to cli
    cli.add_command(pack.pack)
    cli.add_command(agent.agent)
    cli.add_command(source.source)
