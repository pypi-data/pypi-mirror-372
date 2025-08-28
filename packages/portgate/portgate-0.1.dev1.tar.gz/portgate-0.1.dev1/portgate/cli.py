#!/usr/bin/env python3

import argparse
import sys
import signal
import time
from typing import Optional

from .core import PortGate
from .exceptions import PortGateError


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portgate",
        description="A command-line utility to manage port mappings on your local router using UPnP/NAT-PMP.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""description:
'PortGate' makes it easy to open, close, and list ports to expose local services
(web servers, game servers, etc.) to the internet using UPnP/NAT-PMP protocols.

examples:
  portgate 8080
      \u2192 Quick mode: Maps an available external port to internal port 8080 (infinite TTL)

  portgate add -p 8080 -P TCP -t 0
      \u2192 Maps TCP 8080 on WAN to 8080 on local host, permanent until reboot

  portgate add -p 25565 -P TCP -e 50000
      \u2192 Maps external port 50000 \u2192 internal port 25565

  portgate remove -p 8080 -P TCP
      \u2192 Removes TCP port 8080 mapping

  portgate list
      \u2192 Lists current UPnP/NAT-PMP mappings

  portgate info
      \u2192 Displays router info and your public IP
"""
    )
    
    parser.add_argument("quick_port", nargs="?", type=int, help="Quick mode: Internal port to forward (automatically finds external port)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands", metavar="{add,remove,list,refresh,clear,info}")
    
    add_parser = subparsers.add_parser("add", help="Open a new port mapping")
    add_parser.add_argument("-p", "--port", type=int, required=True, help="Internal port to forward (e.g., 8080)")
    add_parser.add_argument("-e", "--external", type=int, help="External port (default = same as internal)")
    add_parser.add_argument("-P", "--protocol", choices=["TCP", "UDP", "BOTH"], default="TCP", help="Protocol: TCP, UDP, or BOTH (default: TCP)")
    add_parser.add_argument("-d", "--desc", default="PortGate", help='Description for the mapping (default: "PortGate")')
    add_parser.add_argument("-t", "--ttl", type=int, default=3600, help="Lease duration in seconds (0 = infinite, default: 3600)")
    
    remove_parser = subparsers.add_parser("remove", help="Remove an existing port mapping")
    remove_parser.add_argument("-p", "--port", type=int, required=True, help="Internal port to remove")
    remove_parser.add_argument("-P", "--protocol", choices=["TCP", "UDP", "BOTH"], default="TCP", help="Protocol: TCP, UDP, or BOTH (default: TCP)")
    
    subparsers.add_parser("list", help="List all active port mappings")
    
    refresh_parser = subparsers.add_parser("refresh", help="Refresh/renew a specific port mapping")
    refresh_parser.add_argument("-p", "--port", type=int, required=True, help="Internal port to refresh")
    refresh_parser.add_argument("-P", "--protocol", choices=["TCP", "UDP", "BOTH"], default="TCP", help="Protocol: TCP, UDP, or BOTH (default: TCP)")
    refresh_parser.add_argument("-t", "--ttl", type=int, default=3600, help="Lease duration in seconds (0 = infinite, default: 3600)")
    
    subparsers.add_parser("clear", help="Remove all port mappings created by this tool")
    
    subparsers.add_parser("info", help="Show router & WAN IP info")
    
    return parser


def find_available_port(portgate: PortGate, start_port: int = 1024, max_port: int = 65535) -> int:
    existing_mappings = portgate.list_mappings()
    used_ports = {mapping['external_port'] for mapping in existing_mappings}
    
    for port in range(start_port, max_port + 1):
        if port not in used_ports:
            return port
    
    raise PortGateError("No available ports found")


def handle_quick_mode(internal_port: int):
    try:
        portgate = PortGate()
        
        external_port = find_available_port(portgate)
        
        portgate.add_mapping(
            internal_port=internal_port,
            external_port=external_port,
            protocol="TCP",
            description="PortGate",
            ttl=0
        )
        
        info = portgate.get_router_info()
        wan_ip = info['wan_ip']
        
        print(f"Port forwarding established!")
        print(f"External address: {wan_ip}:{external_port}")
        print(f"Internal address: localhost:{internal_port}")
        print(f"Press Ctrl+C to stop forwarding...")
        
        def signal_handler(sig, frame):
            print(f"\nRemoving port mapping {external_port} -> {internal_port}...")
            try:
                portgate.remove_mapping(internal_port=internal_port, protocol="TCP")
                print("Port mapping removed successfully.")
            except Exception as e:
                print(f"Error removing port mapping: {e}")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
            
    except PortGateError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
        handle_quick_mode(port)
        return
    
    parser = create_parser()
    args = parser.parse_args()
    
    if args.quick_port is not None:
        handle_quick_mode(args.quick_port)
        return
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        portgate = PortGate()
        
        if args.command == "add":
            external_port = args.external if args.external is not None else args.port
            portgate.add_mapping(
                internal_port=args.port,
                external_port=external_port,
                protocol=args.protocol,
                description=args.desc,
                ttl=args.ttl
            )
            print(f"Successfully added port mapping: {args.protocol} {external_port} -> {args.port}")
            
        elif args.command == "remove":
            portgate.remove_mapping(
                internal_port=args.port,
                protocol=args.protocol
            )
            print(f"Successfully removed port mapping: {args.protocol} {args.port}")
            
        elif args.command == "list":
            mappings = portgate.list_mappings()
            if mappings:
                print("Active port mappings:")
                for mapping in mappings:
                    print(f"  {mapping['protocol']} {mapping['external_port']} -> {mapping['internal_client']}:{mapping['internal_port']} ({mapping['description']})")
            else:
                print("No active port mappings found.")
                
        elif args.command == "refresh":
            portgate.refresh_mapping(
                internal_port=args.port,
                protocol=args.protocol,
                ttl=args.ttl
            )
            print(f"Successfully refreshed port mapping: {args.protocol} {args.port}")
            
        elif args.command == "clear":
            count = portgate.clear_mappings()
            print(f"Successfully removed {count} port mappings.")
            
        elif args.command == "info":
            info = portgate.get_router_info()
            print("Router Information:")
            print(f"  WAN IP Address: {info['wan_ip']}")
            print(f"  LAN Address: {info['lan_addr']}")
            print(f"  WAN Address: {info['wan_addr']}")
            
    except PortGateError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()