# 📂 Groupie — Command-Line File Grouper with Missing File Management

> Organize your scattered files into logical, virtual groups without moving or copying them.  
> Easily track missing files with warnings and clean up your groups directly from the CLI.

---

## ✨ Key Features

- **Virtual File Grouping:** Create named groups of files tracked by absolute paths, without modifying the original files or directory structure.
- **Smart Group Management:** Files can only belong to one group at a time, with automatic handling when adding to a new group.
- **Missing File Detection:** When listing groups, any file paths that no longer exist on disk are flagged with a red asterisk (*), helping you quickly identify broken references.
- **Optional Auto-Cleanup on Listing:** Use the `--clean` (or `-c`) flag with the listing command to automatically remove missing files during display.
- **Dedicated Cleanup Command:** Run `gr clean` to scan all groups for missing files and remove them after an explicit user confirmation. Add the `-y` flag to skip confirmation and clean automatically.
- **Cross-Platform Compatibility:** Works consistently on Windows, macOS, and Linux.
- **Color-Coded Output:** Files are displayed with colors based on their type, similar to the Linux `ls` command.
- **Lightweight Storage:** Uses a simple JSON file stored at `~/.file_groups.json` to maintain your groups, making it easy to back up, edit, or migrate.
- **Intuitive CLI Interface:** Short commands and flags designed for speed and simplicity in terminal workflows.

## 🚀 Installation

### From PyPI (Coming Soon)

```bash
# Install from PyPI (once published)
pip install groupie
```

### From GitHub Repository

```bash
# Install directly from GitHub
pip install git+https://github.com/nicotegui/groupie.git
```

### From Source

```bash
# Clone the repository
git clone https://github.com/nicotegui/groupie.git
cd groupie

# Install
pip install .
```

### Important: Adding to PATH (Windows)

After installation, you might see this warning:
```
WARNING: The script gr.exe is installed in 'C:\Users\username\AppData\Roaming\Python\Python312\Scripts' which is not on PATH.
```

To resolve this and use `gr` from anywhere, you have three options:

#### Option 1: Add to PATH for current session only

```powershell
# PowerShell (replace 'username' and Python version as needed)
$env:Path += ";C:\Users\username\AppData\Roaming\Python\Python312\Scripts"
```

```cmd
:: Command Prompt (replace 'username' and Python version as needed)
set PATH=%PATH%;C:\Users\username\AppData\Roaming\Python\Python312\Scripts
```

#### Option 2: Add to PATH permanently

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", select "Path" and click "Edit"
5. Click "New" and add the path from the warning message
6. Click "OK" on all dialog boxes
7. Restart your terminal

#### Option 3: Use the full path

If you don't want to modify your PATH, you can use the full path to the executable:

```powershell
C:\Users\username\AppData\Roaming\Python\Python312\Scripts\gr.exe create my-group
```

### Linux and macOS

On Unix-like systems, pip typically installs scripts in a location that's already in your PATH, so the `gr` command should work immediately.

## 🖥 Command Reference

| Command | Description | Notes |
|---------|-------------|-------|
| `gr create NAME` | Create a new group with the given name | Fails if group already exists |
| `gr add NAME FILE...` | Add one or more files to the specified group | Accepts relative or absolute file paths |
| `gr ls` | List files in current directory and all groups | Shows both directory contents and groups |
| `gr ls --clean` / `-c` | List and remove missing files automatically | Shows removals after listing |
| `gr ls --no-files` / `-n` | List only groups without directory files | Use when only interested in groups |
| `gr clean` | Remove missing files from all groups | Prompts for confirmation before deleting |
| `gr clean -y` | Same as above but auto-confirms | Useful for scripting |
| `gr remove-group NAME` | Remove a group entirely | |
| `gr remove-file GROUP FILE` | Remove a specific file from a group | |

## 📋 Usage Examples

### Create a new group

```bash
gr create project-docs
```

### Add files to a group

```bash
gr add project-docs ~/Documents/report.docx ./notes.txt /path/to/data.csv
```

### List all groups and files

```bash
gr ls
```

Sample output:

```plaintext
Files in current-directory:
  README.md setup.py test_file.txt test_groupie.py

Groups:
  project-docs:
    report.docx notes.txt
  references:
    data.csv
```

### List only groups (without directory files)

```bash
gr ls -n
```

Sample output:

```plaintext
Groups:
  project-docs:
    report.docx notes.txt
  references:
    data.csv
```
  notes.txt (missing)
  data.csv
```

### List and auto-clean missing files

```bash
gr ls --clean
```

Sample output:

```plaintext
Files in current-directory:
  README.md setup.py test_groupie.py

Groups:
  project-docs:
    report.docx notes.txt*

Legend: * = missing file

Removed 1 missing file(s)
```

### Remove missing files from all groups

```bash
gr clean
```

Sample output:

```plaintext
Found 1 missing file(s) in 1 group(s):

demo:
  test_file.txt*

Legend: * = missing file

Do you want to remove these missing files? [y/N]: y
Removed 1 missing file(s) from 1 group(s)
```

### Remove missing files without confirmation

```bash
gr clean -y
```

Sample output:

```plaintext
Removed 2 missing file(s) from 2 group(s)
```

## 🔧 Storage

Your groups are stored in a JSON file at `~/.file_groups.json`. You can easily back up, edit, or migrate this file if needed.

## 📜 License

MIT License
