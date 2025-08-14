This is a command-line tool called Groupie for managing virtual file groups:

- Create named groups of files without moving or copying them
- Automatically detect missing files
- Clean up missing files from groups
- Cross-platform compatibility (Windows, macOS, Linux)

The tool is implemented as a Python CLI application using Click.

Key files:
- `groupie/core.py`: Core functionality for managing file groups
- `groupie/cli.py`: Command-line interface using Click
- `setup.py`: Package setup for installation

The main command is `gr` with subcommands:
- `gr create NAME`: Create a new group
- `gr add NAME FILE...`: Add files to a group
- `gr ls`: List all groups
- `gr ls --clean`: List and remove missing files
- `gr clean`: Clean missing files with confirmation
- `gr clean -y`: Clean missing files without confirmation
- `gr remove-group NAME`: Remove a group
- `gr remove-file GROUP FILE`: Remove a file from a group
