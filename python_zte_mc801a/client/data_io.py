import yaml
import json
from pathlib import Path
from datetime import datetime
import logging

log = logging.getLogger("rich")


def check_config(router_ip: str, password: str) -> dict:
    setting_file_config = False
    cli_argument_config = False

    config = None

    if router_ip and password:
        log.info("Configuration from CLI options")
        return {"router_ip": router_ip, "password": password}
    elif router_ip or password:
        log.info("Both router-ip and password CLI options must be provided")
    elif Path("settings.json").exists():
        with open("settings.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        if (
            (config is not None)
            & ("password" in config.keys())
            & ("router_ip" in config.keys())
        ):
            log.info(f"Configuration from file: {Path('settings.json')}")
            setting_file_config = True
            return config
    else:
        log.error(f"Could not locate settings file or CLI settings parameters.")

    return None


def check_create_data_file():
    if not Path("data.json").exists():
        Path("data.json").touch()
        Path("data.json").write_text('{"signal_data":[]}')


def persist_data(data):
    if data:
        check_create_data_file()

        with open("data.json", "r") as f:
            existing_json_data = json.load(f)

        with open("data.json", "w") as f:
            data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            existing_json_data["signal_data"].append(data)

            json.dump(existing_json_data, f)


def load_data():
    check_create_data_file()

    with open("data.json", "r") as f:
        json_data = json.load(f)

        if "signal_data" in json_data.keys():
            y = [int(x["lte_rsrp"]) for x in json_data["signal_data"][-10:]]
            x = [*range(0, len(y))]

            return x, y

        else:
            return [], []
