import json
import os
from datetime import datetime
from pathlib import Path
from time import sleep

import typer
import yaml
from rich import print
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from python_zte_mc801a.lib.data_processing import process_data
from python_zte_mc801a.lib.router_requests import (
    get_auth_cookies,
    get_latest_sms_messages,
    get_signal_data,
)

app = typer.Typer()

console = Console()


@app.callback()
def callback():
    """
    ZTE MC801a Management Tool
    """


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body"),
    )
    return layout


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "ZTE MC801a Monitoring Dashboard by [b]@nicjac[/b]",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")


def generate_sms_table(sms_data) -> Table:
    table = Table(show_lines=True)
    table.add_column("Content")
    for msg in sms_data:
        table.add_row(f"{msg['content']}")
    return Panel(table, title="Latest SMS")


# with Progress(TextColumn("{task.description}"), BarColumn(), TextColumn("-{task.completed}db")) as progress:

#     bar_4g = progress.add_task("[b]4G[/b] Signal Strength", total=130, completed=abs(int(data['lte_rsrp'])))
#     bar_5g = progress.add_task("[b]5G[/b] Signal Strength", total=130, completed=abs(int(data['Z5g_rsrp'])))

# layout['side'].update(progress)


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


def check_config() -> dict:
    setting_file_config = False
    cli_argument_config = False

    config = None

    with open("settings.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    if (
        (config is not None)
        & ("password" in config.keys())
        & ("router_ip" in config.keys())
    ):
        return config


@app.command()
def test():
    config = check_config()
    cookies = get_auth_cookies(config["router_ip"], config["password"])
    data = get_signal_data(config["router_ip"], cookies)
    print(data)
    # persist_data(data)


def persist_data(data):
    if data:
        if not Path("data.json").exists():
            Path("data.json").touch()
            Path("data.json").write_text('{"signal_data":[]}')

        with open("data.json", "r") as f:
            existing_json_data = json.load(f)

        with open("data.json", "w") as f:
            data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            existing_json_data["signal_data"].append(data)

            json.dump(existing_json_data, f)


def load_data():
    if Path("data.json").exists():
        with open("data.json", "r") as f:
            json_data = json.load(f)

            y = [int(x["lte_rsrp"]) for x in json_data["signal_data"][-10:]]
            x = [*range(0, len(y))]

            return x, y


def generate_table(
    processed_data, primary_data_type, secondary_data_type=None
) -> Table:
    table = Table(show_lines=True)

    primary_data = processed_data[primary_data_type]

    main_row = []

    for column in primary_data:
        table.add_column(primary_data[column]["desc"])
        main_row.append(str(primary_data[column]["str_value"]))

    table.add_row(*main_row)

    if secondary_data_type and (len(processed_data[secondary_data_type])):
        secondary_data = process_dataed[secondary_data_type]

        for ca_row in secondary_data:
            table.add_row(*ca_row)

    return Panel(table, title=primary_data_type)


def update_live_table(layout, config):
    cookies = get_auth_cookies(config["router_ip"], config["password"])
    data = get_signal_data(config["router_ip"], cookies)
    processed_data = process_data(data)

    layout["side"].update(
        Group(
            generate_table(processed_data, "CELL AND NETWORK"),
            generate_table(processed_data, "4G", "4G_CA"),
            generate_table(processed_data, "5G"),
        )
    )
    # layout["body"].update(generate_sms_table(get_latest_sms_messages(config['router_ip'],cookies)))

    import termplotlib as tpl

    x, y = load_data()

    fig = tpl.figure()
    fig.plot(x, y, ylim=[-98, -90])

    layout["body"].update(Panel(fig.get_string(), title="4G Signal Power"))

    return data, processed_data


def update_footer(layout, processed_data):
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        f"🌡  4G:{processed_data['MISC']['TEMPERATURE_4G']['str_value']}C  -  5G:{processed_data['MISC']['TEMPERATURE_5G']['str_value']}C",
        f"{processed_data['MISC']['FIRMWARE_VERSION']['str_value']}",
    )
    layout["footer"].update(Panel(grid))


@app.command()
def live():
    """Show a live dashboard"""

    config = check_config()

    PERSIST_INTERVAL = 60

    layout = make_layout()
    layout["header"].update(Header())
    data, processed_data = update_live_table(layout, config)
    update_footer(layout, processed_data)

    last_persisted = None

    # Layout automatically refreshed, so just need to update underlying data??

    with Live(layout, refresh_per_second=0.5, screen=True):
        while True:
            data, processed_data = update_live_table(layout, config)
            update_footer(layout, processed_data)

            if (
                not last_persisted
                or (datetime.now() - last_persisted).seconds > PERSIST_INTERVAL
            ):
                last_persisted = datetime.now()
                persist_data(data)

            sleep(5)
            # progress.update(bar_4g, completed=abs(int(data['lte_rsrp'])))
            # progress.update(bar_5g, completed=abs(int(data['Z5g_rsrp'])))


if __name__ == "__main__":
    typer.run(live)
