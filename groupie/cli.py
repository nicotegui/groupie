"""
Command-line interface for Groupie
"""
import os
import sys
import stat
import click
from pathlib import Path
from typing import List, Dict, Tuple

from .core import FileGroupManager


def is_file_executable(file_path: str) -> bool:
    """
    Cross-platform check if a file is executable
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is executable, False otherwise
    """
    if os.name == 'nt':  # Windows
        return file_path.lower().endswith(('.exe', '.bat', '.cmd', '.ps1'))
    else:  # Unix-like
        return os.access(file_path, os.X_OK)


def get_file_color(file_path: str) -> Dict[str, str]:
    """
    Determine color styling for a file based on its type and permissions,
    similar to Linux ls command.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with fg (foreground) and style keys
    """
    if not os.path.exists(file_path):
        return {'fg': 'red', 'bold': True}  # Missing files
    
    # Get file stats
    file_stat = os.stat(file_path)
    mode = file_stat.st_mode
    
    # Check if it's a directory (handled separately)
    if stat.S_ISDIR(mode):
        return {'fg': 'bright_blue', 'bold': True}
    
    # Check if it's executable - use cross-platform method
    is_executable = is_file_executable(file_path)
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    
    # Color scheme similar to common ls implementations
    if is_executable:
        return {'fg': 'bright_green', 'bold': True}  # Executable files
    elif ext in ['.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z']:
        return {'fg': 'bright_red'}  # Archives
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        return {'fg': 'bright_magenta'}  # Images
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
        return {'fg': 'cyan'}  # Audio
    elif ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']:
        return {'fg': 'bright_cyan'}  # Video
    elif ext in ['.py', '.js', '.ts', '.rb', '.php', '.java', '.c', '.cpp', '.h', '.cs', '.go']:
        return {'fg': 'bright_yellow'}  # Code files
    elif ext in ['.md', '.txt', '.log', '.csv', '.json', '.xml', '.html', '.css']:
        return {'fg': 'white'}  # Text files
    else:
        return {'fg': 'white'}  # Default


def format_file_name(file_path: str, basename_only: bool = True, is_missing: bool = False) -> str:
    """
    Format a file name with appropriate color based on file type.
    
    Args:
        file_path: Path to the file
        basename_only: If True, only return the basename
        is_missing: If True, treat as a missing file
        
    Returns:
        Styled file name
    """
    name = os.path.basename(file_path) if basename_only else file_path
    
    if is_missing:
        return click.style(f"{name}*", fg='red', bold=True)
    
    color_opts = get_file_color(file_path)
    return click.style(name, **color_opts)


@click.group()
@click.version_option()
def main():
    """Groupie - Virtual file grouper with missing file management"""
    pass


@main.command()
@click.argument('name')
def create(name: str):
    """Create a new group with the given NAME"""
    manager = FileGroupManager()
    
    if manager.create_group(name):
        click.echo(f"Group '{name}' created successfully")
    else:
        click.echo(f"Error: Group '{name}' already exists", err=True)
        sys.exit(1)


@main.command()
@click.argument('name')
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
def add(name: str, files: List[str]):
    """Add one or more FILES to the specified group NAME"""
    manager = FileGroupManager()
    
    try:
        added, already_in_group = manager.add_files_to_group(name, files)
        
        if added > 0:
            click.echo(f"Added {added} file(s) to group '{name}'")
        
        if already_in_group > 0:
            click.echo(f"{already_in_group} file(s) were already in group '{name}'")
            
        if added == 0 and already_in_group == 0:
            click.echo("No files were added")
            
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command(name="ls")
@click.option('--clean', '-c', is_flag=True, help='Automatically remove missing files during listing')
@click.option('--no-files', '-n', is_flag=True, help='Don\'t display files in the current directory')
def list_command(clean: bool, no_files: bool):
    """List all groups and files, flagging missing files"""
    # Get manager and group data first to identify files in groups
    manager = FileGroupManager()
    groups_with_status = manager.list_groups(clean=clean)
    
    # Get all files that are in groups (to exclude them from non-grouped display)
    files_in_groups = set()
    for group_name, files_with_status in groups_with_status.items():
        for file_path, is_missing in files_with_status:
            if not is_missing:  # Only add existing files
                # Resolve to absolute path for consistent comparison
                abs_path = str(Path(file_path).resolve())
                files_in_groups.add(abs_path)
    
    # Display current directory files if not disabled, excluding those in groups
    if not no_files:
        # Get current directory
        current_dir = os.getcwd()
        
        # List files in the current directory
        try:
            # Get all items in the directory
            all_items = []
            for item in os.listdir(current_dir):
                full_path = os.path.join(current_dir, item)
                abs_path = str(Path(full_path).resolve())
                
                # Only include if not in any group
                if os.path.isfile(full_path) and abs_path not in files_in_groups:
                    # Color-code files based on type/permissions
                    all_items.append(format_file_name(full_path))
                elif os.path.isdir(full_path):
                    # Format directories with appropriate color
                    all_items.append(format_file_name(full_path))
            
            # Sort and display items in columns (similar to 'ls')
            if all_items:
                # Format in columns like standard ls
                click.echo(f"  {' '.join(sorted(all_items))}")
            else:
                click.echo("  (no files)")
        except Exception as e:
            click.echo(f"  Error listing directory: {str(e)}")
    
    # List the groups now
    
    if not groups_with_status:
        click.echo("\nNo groups found. Create one with 'gr create NAME'")
        return
    
    click.echo("\nGroups:")
    
    removed_count = 0
    has_missing_files = False
    
    for group_name, files_with_status in groups_with_status.items():
        click.echo(f"  {group_name}:")
        
        if not files_with_status:
            click.echo("    (empty)")
            continue
            
        # Group all files together with their status suffix
        file_display = []
        
        for file_path, is_missing in files_with_status:
            if is_missing:
                if clean:
                    removed_count += 1
                # Use formatting for missing files
                file_display.append(format_file_name(file_path, is_missing=True))
                has_missing_files = True
            else:
                # Use color-coded formatting based on file type
                file_display.append(format_file_name(file_path))
        
        # Display all files on a single line
        if file_display:
            click.echo(f"    {' '.join(sorted(file_display))}")
        else:
            click.echo("    (empty)")
    
    if clean and removed_count > 0:
        click.echo(f"\nRemoved {removed_count} missing file(s)")
    

@main.command()
@click.option('-y', is_flag=True, help='Skip confirmation and clean automatically')
def clean(y: bool):
    """Remove missing files from all groups"""
    manager = FileGroupManager()
    
    # First check what would be removed
    removed = manager.clean_groups()
    
    if not removed:
        click.echo("No missing files found")
        return
    
    # Count total files to be removed
    total_files = sum(len(files) for files in removed.values())
    
    # If auto-confirm flag not set, ask for confirmation
    if not y:
        click.echo(f"Found {total_files} missing file(s) in {len(removed)} group(s):")
        
        for group_name, file_paths in removed.items():
            click.echo(f"\n{group_name}:")
            file_displays = [format_file_name(path, is_missing=True) for path in file_paths]
            click.echo(f"  {' '.join(sorted(file_displays))}")
        
        # Add legend for the * indicator
        click.echo(f"\nLegend: {click.style('*', fg='red', bold=True)} = missing file")
        
        if not click.confirm("\nDo you want to remove these missing files?"):
            click.echo("Operation cancelled")
            return
        
        # Re-run the clean operation now that we have confirmation
        removed = manager.clean_groups()
    
    # Display removal summary
    click.echo(f"Removed {total_files} missing file(s) from {len(removed)} group(s)")


@main.command('remove-group')
@click.argument('name')
def remove_group(name: str):
    """Remove a group"""
    manager = FileGroupManager()
    
    if manager.remove_group(name):
        click.echo(f"Group '{name}' removed")
    else:
        click.echo(f"Error: Group '{name}' not found", err=True)
        sys.exit(1)


@main.command('remove-file')
@click.argument('group_name')
@click.argument('file', type=click.Path())
def remove_file(group_name: str, file: str):
    """Remove a file from a group"""
    manager = FileGroupManager()
    
    try:
        if manager.remove_file_from_group(group_name, file):
            click.echo(f"File removed from group '{group_name}'")
        else:
            click.echo(f"Error: File not found in group '{group_name}'", err=True)
            sys.exit(1)
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
