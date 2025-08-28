# PortGate

[![PyPI](https://img.shields.io/pypi/v/portgate)](https://pypi.org/project/portgate/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/portgate)](https://pypi.org/project/portgate/)
[![PyPI - License](https://img.shields.io/pypi/l/portgate)](https://pypi.org/project/portgate/)
[![Downloads](https://static.pepy.tech/badge/portgate)](https://pepy.tech/project/portgate)

A command-line utility to manage port mappings on your local router using UPnP/NAT-PMP.
Easily open, close and list ports to expose local services (web servers, game servers, etc.) to the internet without Ngrok, Cloudflare, Serveo, etc.

## Quick Start

Just run the following command to open a port on your router.

```bash
pip install portgate
portgate <local_port>
```

## Features

- Open new port mappings with custom descriptions and TTL
- Remove existing port mappings
- List all active port mappings
- Refresh/renew specific port mappings
- Clear all port mappings created by PortGate
- Display router information and WAN IP

## Installation

Use pip to install PortGate.

```bash
pip install portgate
```

## Usage

### Quick Mode (Recommended)

Just specify the local port you want to forward to the internet.

```bash
portgate <local_port>
```

Example:

```bash
sarp@IdeaPad:~$ portgate 8000
Port forwarding established!
External address: 95.65.xxx.xxx:1025
Internal address: localhost:8000
Press Ctrl+C to stop forwarding...
^C
Removing port mapping 1025 -> 8000...
Port mapping removed successfully.
```

### Command Line Interface

```bash
portgate <command> <options>
```

#### Commands

| Command  | Description                      |
|----------|----------------------------------|
| `add`    | Open a new port mapping          |
| `remove` | Remove an existing port mapping  |
| `list`   | List all active port mappings    |
| `refresh`| Refresh/renew a specific mapping |
| `clear`  | Remove all mappings by PortGate  |
| `info`   | Show router & WAN IP info        |

#### Options for `add`

| Option              | Description                                | Default     |
|---------------------|--------------------------------------------|-------------|
| `-p, --port`        | Internal port to forward                   | *Required*  |
| `-e, --external`    | External port                              | Same as int.|
| `-P, --protocol`    | Protocol: TCP, UDP, or BOTH                | TCP         |
| `-d, --desc`        | Description for the mapping                | "PortGate"  |
| `-t, --ttl`         | Lease duration in seconds (0 = infinite)   | 3600        |

#### Examples

```bash
# Map TCP port 8080 on WAN to port 8080 on local host, permanent
portgate add -p 8080 -P TCP -t 0

# Map external port 50000 to internal port 25565
portgate add -p 25565 -P TCP -e 50000

# Remove TCP port 8080 mapping
portgate remove -p 8080 -P TCP

# List current UPnP/NAT-PMP mappings
portgate list

# Display router info and public IP
portgate info
```


## How It Works

PortGate uses the `miniupnpc` Python library to communicate with your router via UPnP/NAT-PMP protocols. This allows you to:

1. Run a service on a specific port locally (e.g., `python3 -m http.server 55000`)
2. Use PortGate to create a port mapping through your router
3. Access your service from the internet using your WAN IP and the mapped port

## Requirements

- Python 3.8 or higher
- `miniupnpc` Python library
- Router with UPnP/NAT-PMP enabled