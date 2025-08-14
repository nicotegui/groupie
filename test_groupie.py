#!/usr/bin/env python
"""
Test script for Groupie
"""
import os
import tempfile
import pathlib
import json
from groupie.core import FileGroupManager

# Create a test storage file with valid JSON
storage_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
storage_file.close()

try:
    # Initialize with empty JSON object
    with open(storage_file.name, 'w') as f:
        json.dump({}, f)
    
    # Create a manager with our test storage
    manager = FileGroupManager(storage_file.name)
    
    # Create test files
    test_dir = tempfile.TemporaryDirectory()
    file1 = pathlib.Path(test_dir.name) / "file1.txt"
    file2 = pathlib.Path(test_dir.name) / "file2.txt"
    file3 = pathlib.Path(test_dir.name) / "file3.txt"
    
    with open(file1, 'w') as f:
        f.write("Test file 1")
    with open(file2, 'w') as f:
        f.write("Test file 2")
    with open(file3, 'w') as f:
        f.write("Test file 3")
    
    # Test group creation
    print("Creating test groups...")
    manager.create_group("docs")
    manager.create_group("data")
    
    # Test adding files
    print("Adding files to groups...")
    manager.add_files_to_group("docs", [str(file1), str(file2)])
    manager.add_files_to_group("data", [str(file2), str(file3)])
    
    # List groups
    print("\nListing all groups:")
    groups = manager.list_groups()
    for group_name, files_with_status in groups.items():
        print(f"\n{group_name}:")
        for file_path, is_missing in files_with_status:
            basename = os.path.basename(file_path)
            status = " (missing)" if is_missing else ""
            print(f"  {basename}{status}")
    
    # Create a missing file by removing file2
    os.remove(file2)
    print("\nRemoved file2.txt to simulate a missing file")
    
    # List groups with missing files
    print("\nListing groups with missing files:")
    groups = manager.list_groups()
    for group_name, files_with_status in groups.items():
        print(f"\n{group_name}:")
        for file_path, is_missing in files_with_status:
            basename = os.path.basename(file_path)
            status = " (missing)" if is_missing else ""
            print(f"  {basename}{status}")
    
    # Clean groups
    print("\nCleaning missing files:")
    removed = manager.clean_groups()
    for group_name, files in removed.items():
        print(f"{group_name}: removed {len(files)} file(s)")
    
    # List after cleaning
    print("\nListing groups after cleaning:")
    groups = manager.list_groups()
    for group_name, files_with_status in groups.items():
        print(f"\n{group_name}:")
        if not files_with_status:
            print("  (empty)")
            continue
        for file_path, is_missing in files_with_status:
            basename = os.path.basename(file_path)
            status = " (missing)" if is_missing else ""
            print(f"  {basename}{status}")

finally:
    # Clean up
    os.unlink(storage_file.name)
    try:
        test_dir.cleanup()
    except:
        pass
    
print("\nTest completed!")
