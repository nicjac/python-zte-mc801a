import typer
import yaml

from python_zte_mc801a.lib.data_processing import process_data
from python_zte_mc801a.lib.router_requests import get_auth_cookies, get_signal_data

from python_zte_mc801a.lib.helpers import force_5g_pci_selection

from python_zte_mc801a.client.live import show_live, LIVE_VISUALIZATIONS

from python_zte_mc801a.client.data_io import check_config

from rich.pretty import pprint
from rich.console import Console
from rich.prompt import Prompt
from rich.padding import Padding

from python_zte_mc801a.lib.constants import ALL_5G_BANDS

import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

app = typer.Typer()

console = Console()


@app.callback()
def callback():
    """
    ZTE MC801a Management Tool
    """


@app.command()
def setup():
    print(Padding("Setup and persist router IP and password", (1, 1)))

    print(
        Padding(
            "🚨 Your password will be stored as plain-text in `settings.yml`. You can alternatively pass your password directly to the various commands.",
            (1, 1),
        )
    )

    router_ip = Prompt.ask(
        "Enter your router IP",
    )

    password = Prompt.ask(
        "Enter your router password",
        password=True,
    )

    with open("settings.yml", "w") as f:
        yaml.dump({"router_ip": router_ip, "password": password}, f)


@app.command(
    help="Try to connect to a target 5G PCI by alternatively setting 5G bands to one of two sets. Useful when a certain PCI is preferred over another (e.g. for performance reason)"
)
def force_5g_pci(
    target_pci: str = typer.Argument(..., help="PCI to target", metavar="TEXT"),
    band_set_1: str = typer.Argument(
        ...,
        help="First set of bands to alternative between (comma separated, e.g. 1,3,78)",
    ),
    band_set_2: str = typer.Argument(
        ALL_5G_BANDS,
        help="Second set of bands to alternative between (comma separated, e.g. 1,3,78)",
        metavar="TEXT",
    ),
):
    config = check_config()
    cookies = get_auth_cookies(config["router_ip"], config["password"])
    data = get_signal_data(config["router_ip"], cookies)
    processed_data = process_data(raw_data=data)

    force_5g_pci_selection(
        target_pci=target_pci,
        processed_data=processed_data,
        router_ip=config["router_ip"],
        auth_cookies=cookies,
        bands_5g=[band_set_1, band_set_2],
    )


@app.command()
def data():
    """Show signal data"""
    config = check_config()
    cookies = get_auth_cookies(config["router_ip"], config["password"])
    data = get_signal_data(config["router_ip"], cookies)
    processed_data = process_data(raw_data=data)
    pprint(processed_data)


@app.command()
def live(
    viz: LIVE_VISUALIZATIONS = typer.Option(
        LIVE_VISUALIZATIONS.SMS, case_sensitive=False
    )
):
    """Show a live dashboard"""

    config = check_config()

    show_live(config, viz=viz)


if __name__ == "__main__":
    typer.run(live)
