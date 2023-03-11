from python_zte_mc801a.lib.router_requests import (
    set_5g_band,
    get_signal_data,
    get_auth_cookies,
    get_latest_sms_messages,
)
from python_zte_mc801a.lib.data_processing import process_data
from python_zte_mc801a.lib.constants import ALL_5G_BANDS
import time
import logging


log = logging.getLogger("rich")


def get_sms_data(router_ip: str, password: str) -> list:
    """Helper method to return SMS data in a single operation

    Args:
        router_ip (str): IP (or hostname) of the router
        user_password (str): Admin user password

    Returns:
        list: list of dictionaries containing SMS data
    """

    auth_cookies = get_auth_cookies(router_ip=router_ip, user_password=password)
    return get_latest_sms_messages(router_ip=router_ip, auth_cookies=auth_cookies)


def get_processed_data(router_ip: str, password: str) -> dict:
    """Helper method to return processed data in a single operation

    Args:
        router_ip (str): IP (or hostname) of the router
        user_password (str): Admin user password

    Returns:
        dict: Processed signal data
    """
    auth_cookies = get_auth_cookies(router_ip=router_ip, user_password=password)
    data = get_signal_data(router_ip=router_ip, auth_cookies=auth_cookies)
    processed_data = process_data(raw_data=data)
    return processed_data, data


def force_5g_pci_selection(
    target_pci: str,
    processed_data: dict,
    router_ip: str,
    auth_cookies: dict,
    bands_5g: list = ["78", ALL_5G_BANDS],
) -> bool:
    """Force selection of a 5G PCI site by alternatively forcing different bands. This is useful if, for example, the router tends to alternate between two PCIs, one significantly outperforming the other.

    Args:
        target_pci (str): The target PCI
        processed_data (dict): Processed signal data
        router_ip (str): Router IP
        auth_cookies (dict): Authentication cookies
        bands_5g (list, optional): The 5G bands to alternate between. Must be a list with two strings (e.g. ["78",["3+78"]]). Defaults to ["78", ALL_5G_BANDS].

    Returns:
        bool: Success
    """
    next_5g_band_set = 0

    for attempt in range(0, 10):
        log.info(f"Attempt {attempt+1} / {10} to obtain target PCI")
        if processed_data["5G"]["PCI"]["str_value"] == target_pci:
            log.info(f"PCI already set to target {target_pci}")
            return True
        else:
            if next_5g_band_set == 0:
                next_5g_band_set = 1
            else:
                next_5g_band_set = 0

            set_5g_band(
                router_ip=router_ip,
                auth_cookies=auth_cookies,
                bands=bands_5g[next_5g_band_set],
            )

            # log.info(f"Setting 5G bands to {bands_5g[next_5g_band_set]}")
            log.info(f"⌛ Waiting 20 seconds before checking current PCI")
            time.sleep(20)

            raw_data = get_signal_data(router_ip=router_ip, auth_cookies=auth_cookies)
            new_processed_data = process_data(raw_data)

            if not new_processed_data["5G"]["PCI"]["str_value"] == target_pci:
                log.info(
                    f'🛑 Not achieved target PCI - current is {new_processed_data["5G"]["PCI"]["str_value"]}'
                )
            else:
                log.info(
                    f'🟢 Achieved target PCI {new_processed_data["5G"]["PCI"]["str_value"]}'
                )
                return True

    return False
