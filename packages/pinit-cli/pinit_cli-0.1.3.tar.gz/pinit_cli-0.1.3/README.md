# pinit: The Smart Python Project Initializer

`pinit` is a command-line tool that streamlines the process of starting and managing Python projects. It handles everything from creating a clean project structure and virtual environment to intelligently managing dependencies and running scripts.

It's designed to be a simple, all-in-one replacement for manually running `venv`, `pip install`, `pip freeze`, and managing `requirements.txt`.

## Features

- **Interactive Setup:** A wizard guides you through creating a new project.
- **Automatic Venv:** Creates a `venv` and upgrades `pip` for you.
- **Smart Dependency Management:** `install` and `uninstall` commands automatically update both a high-level `project.json` and a complete `requirements.txt`.
- **Intelligent Uninstall:** Removing a package also removes its dependencies, *unless* they are required by another package in your project.
- **Script Runner:** Run custom commands defined in your `project.json` with `pinit run <script-name>`.
- **Activated Shell:** Jump into an activated virtual environment shell with the `pinit shell` command.

## Installation

You can install `pinit` directly from PyPI:

```bash
pip install pinit-cli
```

## Usage

### 1. Initialize a New Project

To start a new project, simply run `pinit` in the directory where you want to create it. The interactive wizard will handle the rest.

```bash
pinit
```

### 2. Manage Packages

`pinit` automatically detects and uses the local `venv` for all package operations.

```bash
# Add one or more new packages to the project
pinit install requests flask

# Uninstall a package and its orphaned dependencies
pinit uninstall flask

# Re-install all dependencies from project files
pinit install
```

### 3. Run Scripts

You can define custom script shortcuts in the `scripts` section of your `project.json` file.

```json
// project.json
{
  ...
  "scripts": {
    "start": "python main.py",
    "test": "pytest"
  },
  ...
}
```

Run them from your terminal:

```bash
# Runs "python main.py" using the venv's interpreter
pinit run start

# Runs "pytest"
pinit run test
```

### 4. Use an Activated Shell

For interactive work or debugging, you can launch a new shell session with the virtual environment already activated.

```bash
pinit shell
```
Your terminal prompt will change, indicating you are inside the venv. Type `exit` to return to your normal shell.
