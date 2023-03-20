# python-zte-mc801a

Python client for the ZTE MC801a router.

![Python ZTE MC801a Live View](docs/images/live-view.png?raw=true "Live View")

## What is this?

This is a library and a simple CLI client application to interact with the ZTE MC801A router. The idea is to provide read access to the data made available by the firmware and, in the future, provide functionality to carry out actions such as cell or band locking.

Original idea and inspiration for this project was the very helpful Javascript code provided by [Miononno](https://miononno.it/).

## ⚠️ Warning

**This is not an official client for the router. The authors have no affiliation with the manufacturer**. While most READ operations are likely to be safe, WRITE operations such as cell locking could lead to router malfunction or, in extreme cases, render the device inoperable.

## Features

The table below summarizes the features currently implemented and those being worked on.

| Feature                    | Type  | Status |
| -------------------------- | ----- | ------ |
| Cell information           | READ  | ✅     |
| Network information        | READ  | ✅     |
| 4G signal data             | READ  | ✅     |
| 5G signal data             | READ  | ✅     |
| Carrier Aggregation status | READ  | ✅     |
| SMS view                   | READ  | ✅     |
| 4G band locking            | WRITE | WIP    |
| 5G band locking            | WRITE | ✅     |
| Cell locking               | WRITE | WIP    |

## Compatibility

| Firmware                | Operator | Status               |
| ----------------------- | -------- | -------------------- |
| BD_UKH3GMC801AV1.0.0B15 | Three UK | All features working |

## Getting Started

### Installation

The easiest way to install this package is through `pip`.

```bash
pip install python-zte-mc801a
```

You can also install directly from the repository:

```bash
pip install git+https://github.com/nicjac/python-zte-mc801a
```

### Using the CLI client

In general, the `--help` option will provide more information about client and subcommand usage. For example:

```bash
python-zte-mc801a --help
```

The client requires two parameters to work: the router ip and its admin password. All commands accept `--router-ip` and `--password` options. For example, the following command will return processed data from the router:

```bash
python-zte-mc801a data --router-ip 192.168.0.1 --password ADMIN_PASSWORD
```

Alternatively, one can get the client to create a settings file to persist those options so that commands can be called directly in the future. This is done like so:

```bash
python-zte-mc801a setup
```

The client provides a live view of key router data:

```bash
python-zte-mc801a live --router-ip 192.168.0.1 --password ADMIN_PASSWORD
```
