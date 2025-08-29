import argparse
import shutil
from pathlib import Path
from importlib.resources import files
from importlib.resources.abc import Traversable
from scoutsdk.cli.modules.base_module import BaseModule
from ..error_handler import ValidationError, logger
from scoutsdk.cli.config import Config


class InitModule(BaseModule):
    def __init__(self, config: Config) -> None:
        self.config = config

    def get_command(self) -> str:
        return "init"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        project_parser = subparsers.add_parser(
            self.get_command(), help="Creates an empty scout custom function project"
        )

        project_parser.add_argument(
            "-f",
            "--function",
            help="Initialize a new Scout function project",
            action="store_true",
        )

        project_parser.add_argument(
            "-a",
            "--assistant",
            help="Initialize a new Scout assistant project",
            action="store_true",
        )

        project_parser.add_argument(
            "-m",
            "--micro-app",
            help="Initialize a new Scout Micro App project",
            action="store_true",
        )

        project_parser.add_argument(
            "-d",
            "--destination",
            help="Destination folder for the new project",
            required=True,
        )

        project_parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace) -> None:
        self._init_project(args)

    def _copy_item(self, item: Traversable, dest_path: Path) -> None:
        """Copy a file or directory while ignoring __init__.py and __pycache__ files."""
        if item.name in ["__init__.py", "__pycache__"]:
            return

        if item.is_file():
            shutil.copy2(str(item), dest_path)
        else:
            shutil.copytree(
                str(item),
                dest_path / item.name,
                ignore=shutil.ignore_patterns("__init__.py", "__pycache__", "*.pyc"),
            )

    def _init_project(self, args: argparse.Namespace) -> None:
        # Create the Path object for the destination
        destination = args.destination
        dest_path = Path(destination)

        # Create the directory if it doesn't exist
        if not dest_path.exists():
            dest_path.mkdir(parents=True)
            logger.debug(f"Created directory: {destination}")

        # Check if the directory is empty
        if any(dest_path.iterdir()):
            raise ValidationError(
                f"Destination directory '{destination}' is not empty. "
                "Please choose an empty or non-existent directory."
            )

        data_path = files("scoutsdk.data")

        args_function = args.function
        args_assistant = args.assistant
        args_micro_app = args.micro_app

        if not args_function and not args_assistant and not args_micro_app:
            args_function = True
            args_assistant = True
            args_micro_app = True

        shutil.copy2(str(data_path / ".env.template"), dest_path)

        # Copy files based on the selected options
        if args_function:
            function_path = dest_path / "functions"
            function_path.mkdir(exist_ok=True)
            functions_path = data_path / "functions"
            for item in functions_path.iterdir():
                self._copy_item(item, function_path)

        if args_assistant:
            assistant_path = dest_path / "assistant"
            assistant_path.mkdir(exist_ok=True)
            assistants_path = data_path / "assistants"
            for item in assistants_path.iterdir():
                self._copy_item(item, assistant_path)

        if args_micro_app:
            micro_app_path = dest_path / "micro-app"
            micro_app_source_path = data_path / "micro-app"
            micro_app_path.mkdir(exist_ok=True)
            for item in micro_app_source_path.iterdir():
                self._copy_item(item, micro_app_path)

        logger.info(f"Successfully initialized project in {destination}")
