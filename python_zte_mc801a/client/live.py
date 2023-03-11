from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from time import sleep

from python_zte_mc801a.client.data_io import persist_data, load_data
from python_zte_mc801a.lib.helpers import get_processed_data, get_sms_data

from enum import Enum

import termplotlib as tpl


# with Progress(TextColumn("{task.description}"), BarColumn(), TextColumn("-{task.completed}db")) as progress:

#     bar_4g = progress.add_task("[b]4G[/b] Signal Strength", total=130, completed=abs(int(data['lte_rsrp'])))
#     bar_5g = progress.add_task("[b]5G[/b] Signal Strength", total=130, completed=abs(int(data['Z5g_rsrp'])))

# layout['side'].update(progress)


class LIVE_VISUALIZATIONS(str, Enum):
    POWER_5G = "power-5g"
    POWER_4G = "power-4g"
    SMS = "SMS"


class Header:
    """Display app header."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "ZTE MC801a Monitoring Dashboard by [b]@nicjac[/b]",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")


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


def generate_sms_table(sms_data: list) -> Table:
    """Generate table containing latest SMS messages

    Args:
        sms_data (list): List of dictionaries representing SMS message data

    Returns:
        Table: the SMS message table
    """
    table = Table(show_lines=True)
    table.add_column("Content")
    for msg in sms_data:
        table.add_row(f"{msg['content']}")
    return Panel(table, title="Latest SMS")


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
        secondary_data = processed_data[secondary_data_type]

        for ca_row in secondary_data:
            table.add_row(*ca_row)

    return Panel(table, title=primary_data_type)


def update_live_table(layout, config, viz):
    processed_data, raw_data = get_processed_data(
        config["router_ip"], config["password"]
    )
    layout["side"].update(
        Group(
            generate_table(processed_data, "CELL AND NETWORK"),
            generate_table(processed_data, "4G", "4G_CA"),
            generate_table(processed_data, "5G"),
        )
    )
    # layout["body"].update(

    layout["body"].update(update_viz(config=config, viz=viz))

    return processed_data, raw_data


def update_viz(config: dict, viz: LIVE_VISUALIZATIONS = LIVE_VISUALIZATIONS.SMS):
    if viz == LIVE_VISUALIZATIONS.SMS:
        return generate_sms_table(get_sms_data(config["router_ip"], config["password"]))
    else:
        x, y = load_data()

        fig = tpl.figure()
        fig.plot(x, y, ylim=[-98, -90])

        return Panel(fig.get_string(), title="4G Signal Power")


def update_footer(layout, processed_data):
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        f"🌡  4G:{processed_data['MISC']['TEMPERATURE_4G']['str_value']}C  -  5G:{processed_data['MISC']['TEMPERATURE_5G']['str_value']}C",
        f"{processed_data['MISC']['FIRMWARE_VERSION']['str_value']}",
    )
    layout["footer"].update(Panel(grid))


def show_live(config: dict, viz: LIVE_VISUALIZATIONS):
    layout = make_layout()
    layout["header"].update(Header())
    processed_data, raw_data = update_live_table(layout, config, viz)
    update_footer(layout, processed_data)

    last_persisted = None

    PERSIST_INTERVAL = 60

    # Layout automatically refreshed, so just need to update underlying data??

    with Live(layout, refresh_per_second=0.5, screen=True):
        while True:
            processed_data, raw_data = update_live_table(layout, config, viz)
            update_footer(layout, processed_data)

            if (
                not last_persisted
                or (datetime.now() - last_persisted).seconds > PERSIST_INTERVAL
            ):
                last_persisted = datetime.now()
                persist_data(raw_data)

            sleep(5)
            # progress.update(bar_4g, completed=abs(int(data['lte_rsrp'])))
            # progress.update(bar_5g, completed=abs(int(data['Z5g_rsrp'])))
