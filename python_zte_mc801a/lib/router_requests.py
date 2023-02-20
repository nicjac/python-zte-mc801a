import requests
import hashlib
import codecs
from retry import retry
import logging


@retry(tries=3, delay=2)
def get_auth_cookies(router_ip: str, user_password: str) -> dict:
    """Retrieve authentication cookies from the router

    Args:
        router_ip (str): IP (or hostname) of the router
        user_password (str): Admin user password

    Raises:
        Exception: Unable to retrieve authentication cookies

    Returns:
        dict: Authentication cookies
    """

    # Request the current LD
    r_ld = requests.get(
        f"http://{router_ip}/goform/goform_get_cmd_process?isTest=false&cmd=LD",
        cookies={"stok": ""},
        headers={"referer": f"http://{router_ip}/"},
    )

    # The password is hashed twice
    m = hashlib.sha256()
    m.update(user_password.encode())

    m2 = hashlib.sha256()
    m2.update(f'{m.hexdigest().upper()}{r_ld.json()["LD"]}'.encode())

    pwd = m2.hexdigest().upper()

    # Login request
    r_login = requests.get(
        f"http://{router_ip}/goform/goform_set_cmd_process?isTest=false&goformId=LOGIN&password={pwd}",
        cookies={"stok": ""},
        headers={"referer": f"http://{router_ip}/"},
    )

    if (not "result" in r_login.json().keys()) or (r_login.json()["result"] != "0"):
        raise Exception("Login unsuccessful")

    return r_login.cookies.get_dict()


def get_signal_data(router_ip, auth_cookies) -> dict:
    """Retrieve router data related to signals

    Args:
        router_ip (_type_): IP (or hostname) of the router
        auth_cookies (_type_): Authentication cookies obtained using `get_auth_cookies`

    Returns:
        dict: Signal data dictionary (unprocessed)
    """
    data_to_request = [
        "lte_pci",
        "lte_pci_lock",
        "lte_earfcn_lock",
        "lte_freq_lock",
        "wan_ipaddr",
        "wan_apn",
        "pm_sensor_mdm",
        "pm_modem_5g",
        "nr5g_pci",
        "nr5g_action_band",
        "nr5g_action_channel",
        "Z5g_SINR",
        "Z5g_rsrp",
        "wan_active_channel",
        "wan_active_band",
        "lte_multi_ca_scell_info",
        "cell_id",
        "dns_mode",
        "prefer_dns_manual",
        "standby_dns_manual",
        "rmcc",
        "rmnc",
        "network_type",
        "wan_lte_ca",
        "lte_rssi",
        "lte_rsrp",
        "lte_snr",
        "lte_rsrq",
        "lte_ca_pcell_bandwidth",
        "lte_ca_pcell_band",
        "lte_ca_scell_bandwidth",
        "lte_ca_scell_band",
        "wa_inner_version",
        "cr_version",
        "RD",
        "network_provider",
        "signalbar",
    ]

    r_data = requests.get(
        f'http://{router_ip}/goform/goform_get_cmd_process?isTest=false&cmd={",".join(data_to_request)}&multi_data=1',
        cookies=auth_cookies,
        headers={f"referer": f"http://{router_ip}/"},
    )

    return r_data.json()


def get_latest_sms_messages(router_ip, auth_cookies, n=3) -> list:
    """Retrieve latest SMS messages

    Args:
        router_ip (_type_): IP (or hostname) of the router
        auth_cookies (_type_): Authentication cookies obtained using `get_auth_cookies`
        n (int, optional): Number of messages to retrieve. Defaults to 3.

    Returns:
        list: Dictionaries of messages
    """
    r_data = requests.get(
        f"http://{router_ip}/goform/goform_get_cmd_process?isTest=false&cmd=sms_data_total&page=0&data_per_page=500&mem_store=1&tags=10&order_by=order+by+id+desc",
        cookies=auth_cookies,
        headers={f"referer": f"http://{router_ip}/"},
    )

    json_data = r_data.json()

    messages = json_data["messages"]

    if len(messages) > n:
        messages = messages[0:n]

    # Convert hex representation to binary
    for index, msg in enumerate(messages):
        str_bytes = bytes(msg["content"], encoding="utf-8")
        str_bin = codecs.decode(str_bytes, "hex")
        messages[index]["content"] = str(str_bin, "utf-8")

    return messages
