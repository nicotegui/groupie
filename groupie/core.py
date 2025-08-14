"""
Core functionality for managing file groups
"""
import json
import os
import pathlib
from typing import Dict, List, Set, Tuple, Optional


class FileGroupManager:
    """Manager for virtual file groups"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the file group manager
        
        Args:
            storage_path: Path to the storage file. If None, uses ~/.file_groups.json
        """
        if storage_path is None:
            # Use default location: ~/.file_groups.json
            home_dir = pathlib.Path.home()
            self.storage_path = home_dir / ".file_groups.json"
        else:
            self.storage_path = pathlib.Path(storage_path)
        
        # Initialize empty groups if file doesn't exist
        self.groups: Dict[str, List[str]] = {}
        self._load_groups()
    
    def _load_groups(self) -> None:
        """Load groups from storage file"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.groups = json.load(f)
            
            # Fix any files that might be in multiple groups
            self._fix_duplicate_files()
    
    def _fix_duplicate_files(self) -> None:
        """Ensure each file is only in one group (first group wins)"""
        # Track which files are in which groups
        file_to_group = {}
        changes_made = False
        
        # First pass: identify which files are in which groups
        for group_name, file_paths in self.groups.items():
            for file_path in file_paths.copy():
                if file_path in file_to_group:
                    # File is already assigned to a group, remove from this one
                    self.groups[group_name].remove(file_path)
                    changes_made = True
                else:
                    # First time seeing this file, track it
                    file_to_group[file_path] = group_name
        
        # Save if changes were made
        if changes_made:
            self._save_groups()
            
    def _save_groups(self) -> None:
        """Save groups to storage file"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.groups, f, indent=2)
    
    def create_group(self, name: str) -> bool:
        """Create a new group
        
        Args:
            name: Name of the group
            
        Returns:
            True if created successfully, False if group already exists
        """
        if name in self.groups:
            return False
        
        self.groups[name] = []
        self._save_groups()
        return True
    
    def add_files_to_group(self, group_name: str, file_paths: List[str]) -> Tuple[int, int]:
        """Add files to a group
        
        Args:
            group_name: Name of the group
            file_paths: List of file paths to add
            
        Returns:
            Tuple of (files_added, files_already_in_group)
        """
        if group_name not in self.groups:
            raise KeyError(f"Group '{group_name}' does not exist")
        
        # Convert all paths to absolute paths
        abs_paths = [str(pathlib.Path(path).resolve()) for path in file_paths]
        
        # Track how many files were added vs. already in the group
        added = 0
        already_in_group = 0
        
        # Check if file is in any other group and remove it first
        for path in abs_paths:
            # Check if file exists in any other group
            for other_group, group_files in self.groups.items():
                if other_group != group_name and path in group_files:
                    # Remove from other group
                    self.groups[other_group].remove(path)
            
            # Now add to current group if not already there
            if path not in self.groups[group_name]:
                self.groups[group_name].append(path)
                added += 1
            else:
                already_in_group += 1
        
        self._save_groups()
        return (added, already_in_group)
    
    def list_groups(self, clean: bool = False) -> Dict[str, List[Tuple[str, bool]]]:
        """List all groups with files and missing status
        
        Args:
            clean: If True, removes missing files during listing
            
        Returns:
            Dictionary mapping group names to list of (file_path, is_missing) tuples
        """
        result = {}
        for group_name, file_paths in self.groups.items():
            files_with_status = []
            new_file_list = []
            
            for path in file_paths:
                is_missing = not os.path.exists(path)
                files_with_status.append((path, is_missing))
                
                if not is_missing or not clean:
                    new_file_list.append(path)
            
            result[group_name] = files_with_status
            
            # Update group if cleaning was requested
            if clean and len(new_file_list) != len(file_paths):
                self.groups[group_name] = new_file_list
        
        # Save if changes were made during cleaning
        if clean:
            self._save_groups()
            
        return result
    
    def clean_groups(self) -> Dict[str, List[str]]:
        """Remove missing files from all groups
        
        Returns:
            Dictionary mapping group names to lists of removed file paths
        """
        removed = {}
        
        for group_name, file_paths in self.groups.items():
            new_file_list = []
            removed_files = []
            
            for path in file_paths:
                if os.path.exists(path):
                    new_file_list.append(path)
                else:
                    removed_files.append(path)
            
            if removed_files:
                removed[group_name] = removed_files
                self.groups[group_name] = new_file_list
        
        if removed:
            self._save_groups()
            
        return removed
    
    def remove_group(self, group_name: str) -> bool:
        """Remove a group
        
        Args:
            group_name: Name of the group to remove
            
        Returns:
            True if removed, False if group didn't exist
        """
        if group_name not in self.groups:
            return False
        
        del self.groups[group_name]
        self._save_groups()
        return True
    
    def remove_file_from_group(self, group_name: str, file_path: str) -> bool:
        """Remove a file from a group
        
        Args:
            group_name: Name of the group
            file_path: Path of the file to remove
            
        Returns:
            True if removed, False if file wasn't in group
        """
        if group_name not in self.groups:
            raise KeyError(f"Group '{group_name}' does not exist")
        
        # Convert to absolute path
        abs_path = str(pathlib.Path(file_path).resolve())
        
        if abs_path not in self.groups[group_name]:
            return False
        
        self.groups[group_name].remove(abs_path)
        self._save_groups()
        return True
