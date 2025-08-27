from pathlib import Path

from typer import Option

DEFAULT_ARC_FILE = Path("arc.yaml")

OPTION_ARC_FILE = Option(
    dir_okay=False,
    envvar="LOCARC_FILE",
    exists=True,
    file_okay=True,
    help="Path to locarc spec file to run event stack from",
    resolve_path=True,
)

OPTION_DEFAULT_TIMEOUT = Option(
    envvar="LOCARC_DEFAULT_SUBSCRIPTION_TIMEOUT",
    help="The default timeout to use for waiting subscription to end",
)
