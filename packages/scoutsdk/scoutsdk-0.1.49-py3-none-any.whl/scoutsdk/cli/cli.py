import argparse
import importlib.metadata
from .config import Config, CONFIG_API_ACCESS_TOKEN, CONFIG_API_URL
from .error_handler import handle_exception, set_verbosity
from .modules.chat_completion_module import ChatCompletionModule
from .modules.pkg_module import PkgModule
from .modules.init_module import InitModule
from .modules.sync_module import SyncModule
from ..api.api import ScoutAPI


class ScoutCLI:
    def __init__(self) -> None:
        # Initialize modules
        self.config = Config()
        pkg_module = PkgModule(config=self.config)
        self.modules = [
            InitModule(config=self.config),
            pkg_module,
            ChatCompletionModule(config=self.config),
            SyncModule(config=self.config, pkg_module=pkg_module),
        ]

        # Create command mapping
        self.commands = {
            module.get_command(): module.execute for module in self.modules
        }

        # Get version from package metadata
        version = importlib.metadata.version("scoutsdk")

        # Setup parser
        self.parser = argparse.ArgumentParser(description="Scout CLI")
        self.parser.add_argument("--version", action="version", version=version)
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output with detailed error information",
        )

        # Create subparsers for commands
        subparsers = self.parser.add_subparsers(required=True)

        # Add module-specific parsers
        for module in self.modules:
            module.add_parser(subparsers=subparsers)

    def _create_scout_api(self) -> ScoutAPI:
        api_access_token = self.config.get(CONFIG_API_ACCESS_TOKEN, None)
        api_url = self.config.get(CONFIG_API_URL, None)  # Returns None if not found
        return ScoutAPI(base_url=api_url, api_access_token=api_access_token)

    def execute(self) -> None:
        """Execute the specified command with given arguments"""
        args = self.parser.parse_args()

        # Set verbosity level
        set_verbosity(verbose=args.verbose)

        # Execute the command through the handle_exception decorator
        handle_exception(args.func)(args)


@handle_exception
def main() -> None:
    cli = ScoutCLI()
    cli.execute()
