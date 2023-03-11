import yaml
import json
from pathlib import Path
from datetime import datetime


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


def check_create_config_file():
    if not Path("data.json").exists():
        Path("data.json").touch()
        Path("data.json").write_text('{"signal_data":[]}')


def persist_data(data):
    if data:
        check_create_config_file()

        with open("data.json", "r") as f:
            existing_json_data = json.load(f)

        with open("data.json", "w") as f:
            data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            existing_json_data["signal_data"].append(data)

            json.dump(existing_json_data, f)


def load_data():
    check_create_config_file()

    with open("data.json", "r") as f:
        json_data = json.load(f)

        if "signal_data" in json_data.keys():
            y = [int(x["lte_rsrp"]) for x in json_data["signal_data"][-10:]]
            x = [*range(0, len(y))]

            return x, y

        else:
            return [], []
