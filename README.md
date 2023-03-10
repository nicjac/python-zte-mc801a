# python-zte-mc801a

## What is this?

This is a library and a simple CLI client application to interact with the ZTE MC801A router. The idea is to provide read access to the data made available by the firmware and, in the future, provide functionality to carry out actions such as cell or band locking.

Original idea and inspiration for this project was the very helpful Javascript code provided by [Miononno](https://miononno.it/).

## ⚠️ Warning

This is not an official client for the router. While most READ operations are likely to be safe, WRITE operations such as cell locking could lead to router malfunction or, in extreme cases, render the device inoperable.

## Features

The table below summarizes the features currently implemented and those being worked on.

| Feature                    | Type  | Status |
| -------------------------- | ----- | ------ |
| Cell information           | READ  | ✅     |
| Network information        | READ  | ✅     |
| 4G signal data             | READ  | ✅     |
| 5G signal data             | READ  | ✅     |
| Carrier Aggregation status | READ  | ✅     |
| SMS                        | READ  | ✅     |
| 4G band locking            | WRITE | WIP    |
| 5G band locking            | WRITE | ✅     |
| Cell locking               | WRITE | WIP    |

## Getting Started

### Installation

COMING SOON
