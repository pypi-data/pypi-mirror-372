# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-27

### Added
- Initial release of PortGate
- Command-line interface for managing port mappings
- Quick mode for instant port forwarding (`portgate <port>`)
- Support for UPnP/NAT-PMP protocols
- Add, remove, list, refresh, and clear port mappings
- Router information display

### Features
- Automatically discovers available external ports
- Sets up infinite TTL mappings in quick mode
- Graceful cleanup on Ctrl+C interruption
- Improved error handling with actionable messages
- Optimized startup and operation performance