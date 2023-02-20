import yaml

def check_config() -> dict:

    setting_file_config = False
    cli_argument_config = False

    config = None

    with open('settings.yml','r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    if (config is not None) & ('password' in config.keys()) & ('router_ip' in config.keys()):
        return config
