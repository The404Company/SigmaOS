# SigmaOS
A lightweight and modular command-line interface system with package management capabilities.

## Quick Start
1. Download only the `SigmaOS.py` file to get started
2. Run with: `python SigmaOS.py`
3. Type `help` to see all commands
4. Use `setup` to install essential packages

## System Commands

### Basic Operations
- `help`  - Display help information
- `exit`  - Exit SigmaOS
- `clear` - Clear the terminal screen
- `setup` - Install essential packages
- `reset` - Restore SigmaOS to its default settings

### Package Management
- `ligma list` - List all available packages
- `ligma install <pkg>` - Install a package
- `ligma uninstall <pkg>` - Remove a package
- `<package>` - Execute an installed package

### Alias Management
- `alias list` - Display all configured aliases
- `alias add <name> <cmd>` - Create a new alias
- `alias remove <name>` - Remove an existing alias

## Available Packages

### Essential Tools
- **DoccX** - Document viewer for reading files in the documents directory
- **Yapper** - Lightweight text editor for creating and editing files
- **LigmaUpdate** - Updates all installed packages to their latest versions
- **SigmaUpdate** - Updates the SigmaOS system itself

### System Utilities
- **BetaTask** - System resource monitor and task manager
- **OmegaNet** - Network diagnostics suite with ping, port scanning, and DNS tools
- **Sourcerer** - Package installer for external sources
- **XiAI** - Intelligent assistant designed for SigmaOS

## Keyboard Shortcuts
- `Tab` - Auto-complete commands
- `Up/Down` - Navigate through command history
- `Left/Right` - Move cursor horizontally
- `Ctrl+C` - Interrupt the current operation

## Getting Started
1. Run SigmaOS for the first time
2. Use the `setup` command to install essential packages
3. Use `ligma list` to see all available packages
4. Install additional packages with `ligma install <package>`

## Package Installation Example
```bash
ligma install BetaTask   # Install the system monitor
betatask                 # Run BetaTask
```

## Features
- Smart command auto-completion
- Command history navigation
- Customizable aliases
- Package management system
- Built-in help system
- Modular design with installable packages

## System Requirements
- Python 3.x
- Internet connection for package installation
- Linux or Windows operating system

## Note
You only need to download the `SigmaOS.py` file. The system will automatically:
- Create necessary directories
- Download packages when requested
- Manage dependencies
- Handle updates through packages

All packages and additional features will be downloaded and installed through the built-in package manager when needed.

## Coming Soon

### Planned Features
- SSH client for remote system management
- Custom theme support and color schemes
- Command history search with fuzzy matching

### Upcoming Packages
- **RhoSecure** - Password manager with encription
- **PhiMail**   - Command-line email client
