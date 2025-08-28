import os
import sys
import json
import subprocess
import re
import shlex 

class Logger:
    """Provides styled and colored logging for a professional CLI experience."""
    RESET = "\033[0m"; BOLD = "\033[1m"; RED = "\033[31m"; GREEN = "\033[32m"
    YELLOW = "\033[33m"; BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"

    def _colorize(self, text, color):
        return f"{color}{text}{self.RESET}" if sys.stdout.isatty() else text
    
    def header(self, text): print(self._colorize(f"\n== {text} ==", self.BOLD + self.CYAN))
    def success(self, text): print(f"{self._colorize('[SUCCESS]', self.GREEN)} {text}")
    def info(self, text): print(f"{self._colorize('[INFO]', self.BLUE)} {text}")
    def warning(self, text): print(f"{self._colorize('[WARNING]', self.YELLOW)} {text}")
    def error(self, text): print(f"{self._colorize('[ERROR]', self.RED)} {text}")
    def prompt(self, text): return input(f"{self._colorize('[PROMPT]', self.MAGENTA)} {text} ")

    def status_update(self, text):
        sys.stdout.write(f"  {text}... "); sys.stdout.flush()
    def status_ok(self):
        sys.stdout.write(self._colorize("OK\n", self.GREEN)); sys.stdout.flush()
    def status_fail(self):
        sys.stdout.write(self._colorize("FAILED\n", self.RED)); sys.stdout.flush()

logger = Logger()

def get_python_executable():
    """Determines the correct Python executable to use for pip commands."""
    if sys.prefix != sys.base_prefix:
        return sys.executable, "Using active virtual environment."
    script_dir = "Scripts" if sys.platform == "win32" else "bin"
    local_python_exe = os.path.join("venv", script_dir, "python.exe" if sys.platform == "win32" else "python")
    if os.path.exists(local_python_exe):
        return local_python_exe, "Using locally discovered 'venv' environment."
    return sys.executable, "WARNING: No active or local venv found. Using global Python."

def get_package_dependencies(package_name):
    success, output = run_pip_command(["show", package_name], capture=True)
    if not success:
        return []
    dependencies = []
    for line in output.splitlines():
        if line.startswith("Requires:"):
            deps_str = line.replace("Requires:", "").strip()
            if deps_str:
                dependencies = [dep.strip() for dep in deps_str.split(',')]
            break
    return dependencies

def run_pip_command(args, capture=False):
    """Runs a pip command, streaming output by default, or capturing it if specified."""
    python_exe, reason = get_python_executable()
    if not capture:
        if "WARNING" in reason: logger.warning(reason)
        else: logger.info(reason)
    
    command = [python_exe, "-m", "pip"] + args
    if not capture:
        print(logger._colorize(f"▶ Running: {' '.join(command)}", logger.CYAN))
        print("-" * 50)
    
    try:
        result = subprocess.run(command, check=True, capture_output=capture, text=True)
        if not capture:
            print("-" * 50)
        return True, result.stdout.strip() if capture else ""
    except subprocess.CalledProcessError as e:
        if not capture:
            print("-" * 50)
            logger.error("Pip command failed.")
        return False, e.stderr.strip() if capture else ""
    except FileNotFoundError:
        if not capture:
            logger.error(f"Could not find executable '{python_exe}'.")
        return False, ""

def get_frozen_packages():
    """Runs 'pip freeze' quietly and returns a set of installed packages."""
    python_exe, _ = get_python_executable()
    try:
        result = subprocess.run([python_exe, "-m", "pip", "freeze"], check=True, capture_output=True, text=True)
        return set(result.stdout.strip().splitlines())
    except subprocess.CalledProcessError: return set()

def read_manifest():
    if not os.path.exists("project.json"): return None
    try:
        with open("project.json", "r") as f: return json.load(f)
    except (IOError, json.JSONDecodeError): return None

def write_manifest(data):
    try:
        with open("project.json", "w") as f: json.dump(data, f, indent=2); return True
    except IOError: return False

def handle_install_from_file():
    """Installs dependencies from requirements.txt or project.json."""
    logger.header("Restoring Dependencies")
    if os.path.exists("requirements.txt"):
        logger.info("Found 'requirements.txt', installing from file.")
        if run_pip_command(["install", "-r", "requirements.txt"]):
            logger.success("Dependencies restored successfully.")
        else: sys.exit(1)
    elif os.path.exists("project.json"):
        logger.info("Found 'project.json', generating requirements and installing.")
        manifest = read_manifest()
        if not manifest or "dependencies" not in manifest or not manifest["dependencies"]:
            logger.warning("'project.json' found, but it contains no dependencies. Nothing to install."); return
        reqs = [f"{pkg}=={ver}" for pkg, ver in manifest["dependencies"].items()]
        with open("requirements.txt", "w") as f: f.write("\n".join(reqs))
        logger.success("Generated 'requirements.txt' from 'project.json'.")
        if run_pip_command(["install", "-r", "requirements.txt"]):
            logger.success("Dependencies restored successfully.")
        else: sys.exit(1)
    else:
        logger.error("No 'requirements.txt' or 'project.json' found in this directory."); sys.exit(1)

def handle_install_new_packages(packages_to_install):
    """Installs new packages and saves them to dependency files."""
    logger.header(f"Adding Packages: {', '.join(packages_to_install)}")
    manifest = read_manifest()
    if not manifest:
        logger.error("Cannot add packages: 'project.json' not found."); sys.exit(1)
    packages_before = get_frozen_packages()
    if not run_pip_command(["install"] + packages_to_install):
        logger.error("Aborting dependency update due to installation failure."); sys.exit(1)
    logger.info("Resolving and saving new dependency versions...")
    packages_after = get_frozen_packages()
    logger.status_update("Updating requirements.txt")
    try:
        with open("requirements.txt", "w") as f: f.write("\n".join(sorted(list(packages_after))) + "\n"); logger.status_ok()
    except IOError: logger.status_fail()
    newly_installed = packages_after - packages_before
    if not newly_installed:
        logger.info("Package(s) already installed. Project files are up-to-date."); return
    logger.status_update("Updating project.json")
    requested_set = {p.lower().replace("_", "-") for p in packages_to_install}
    updated = False
    for line in newly_installed:
        match = re.match(r"([^=@\s]+)==([^=@\s]+)", line)
        if match:
            pkg_name, pkg_version = match.groups()
            if pkg_name.lower().replace("_", "-") in requested_set:
                manifest.setdefault("dependencies", {})[pkg_name] = pkg_version
                updated = True
    if updated and write_manifest(manifest): logger.status_ok()
    elif not updated: sys.stdout.write(" (no direct dependencies to add)\n")
    else: logger.status_fail()
    logger.success("Project dependencies updated successfully.")

def calculate_safe_uninstall_list(packages_to_uninstall):
    logger.info("Checking for shared dependencies to prevent accidental removal...")
    
    manifest = read_manifest()
    if not manifest or "dependencies" not in manifest:
        logger.warning("No project.json found or it has no dependencies. Proceeding with standard uninstall.")
        return get_full_dependency_tree(packages_to_uninstall)

    all_direct_deps = set(manifest["dependencies"].keys())
    
    normalized_uninstall_reqs = {p.lower().replace("_", "-") for p in packages_to_uninstall}
    protected_packages = {
        pkg for pkg in all_direct_deps 
        if pkg.lower().replace("_", "-") not in normalized_uninstall_reqs
    }

    if not protected_packages:
        logger.info("No other direct dependencies found. Removing full dependency tree.")
        return get_full_dependency_tree(packages_to_uninstall)

    logger.status_update(f"Analyzing dependencies of {len(protected_packages)} protected package(s)")
    protected_deps_tree = get_full_dependency_tree(protected_packages)
    sys.stdout.write("\n") 

    potential_uninstall_tree = get_full_dependency_tree(packages_to_uninstall)
    
    final_uninstall_list = potential_uninstall_tree - protected_deps_tree
    
    kept_packages = potential_uninstall_tree.intersection(protected_deps_tree)
    if kept_packages:
        logger.success("Analysis complete. The following shared dependencies will be kept:")
        for pkg in sorted(list(kept_packages)):
            print(f"  - {pkg} (required by another package)")

    return final_uninstall_list

def handle_shell():
    """Launches a new shell with the virtual environment activated."""
    logger.header("Launching Activated Shell")
    
    venv_dir = "venv"
    if not os.path.isdir(venv_dir):
        logger.error("No 'venv' directory found. Cannot activate shell.")
        logger.info("Try running the initializer first or creating a venv manually.")
        sys.exit(1)

    if sys.platform == "win32":
        activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
        shell_cmd = f'cmd.exe /k "{activate_script}"'
        logger.info("Launching Windows Command Prompt with venv activated...")
        logger.info("Type 'exit' to close this shell and return.")
    else:
        shell = os.environ.get("SHELL", "/bin/sh")
        activate_script = os.path.join(venv_dir, "bin", "activate")
        logger.info(f"Launching '{os.path.basename(shell)}' with venv activated...")
        logger.info("Type 'exit' or press Ctrl+D to close this shell and return.")
        args = [shell, '-i'] 
        os.environ['VIRTUAL_ENV_PROMPT'] = f"({os.path.basename(os.getcwd())}) "
        subprocess.run(f'source "{activate_script}" && exec "{shell}" -i', shell=True, executable=shell)
        return 
    try:
        subprocess.run(shell_cmd, shell=True)
        logger.success("\nExited activated shell.")
    except Exception as e:
        logger.error(f"Failed to launch shell: {e}")
        sys.exit(1)

def handle_run_script(script_args):
    """Executes a command from the 'scripts' section of project.json."""
    if not script_args:
        logger.error("You must specify which script to run."); logger.info("Example: pinit run start"); return

    script_name = script_args[0]; additional_args = script_args[1:]

    manifest = read_manifest()
    if not manifest: logger.error("'project.json' not found. Cannot run scripts."); sys.exit(1)

    scripts = manifest.get("scripts", {}); command_template = scripts.get(script_name)
    if not command_template:
        logger.error(f"Script '{script_name}' not found in project.json.")
        if scripts: logger.info("Available scripts: " + ", ".join(scripts.keys()))
        sys.exit(1)

    python_exe, _ = get_python_executable()
    if command_template.strip().startswith("python"):
       
        parts = command_template.split(" ", 1)
        command_template = f'"{python_exe}"' + (f' {parts[1]}' if len(parts) > 1 else '')
    
    command_to_run = command_template
    if additional_args:
        command_to_run += " " + " ".join(shlex.quote(arg) for arg in additional_args)

    logger.info(f"Running script '{script_name}': {command_to_run}")
    print()

    try:
        process = subprocess.run(command_to_run, shell=True)
        print()
        if process.returncode != 0:
            logger.warning(f"Script '{script_name}' finished with a non-zero exit code: {process.returncode}")

    except Exception as e:
        logger.error(f"Failed to execute script '{script_name}': {e}"); sys.exit(1)

def handle_uninstall_packages(packages_to_uninstall):
    """
    Uninstalls packages and intelligently removes their dependency tree,
    sparing any dependencies that are required by other packages.
    """
    logger.header(f"Uninstalling Packages: {', '.join(packages_to_uninstall)}")
    
    full_uninstall_list = calculate_safe_uninstall_list(packages_to_uninstall)
    
    if not full_uninstall_list:
        logger.success("All packages requested for removal are dependencies of other project packages. Nothing to uninstall.")
        return

    logger.info("The following packages will be removed:")
    for pkg in sorted(list(full_uninstall_list)):
        print(f"  - {pkg}")
    
    success, _ = run_pip_command(["uninstall", "-y"] + sorted(list(full_uninstall_list)))
    if not success:
        logger.warning("Uninstall command reported an error. This can be okay if some packages were already removed.")

    logger.info("Updating dependency files to reflect removal...")
    packages_after = get_frozen_packages()
    
    logger.status_update("Updating requirements.txt")
    try:
        with open("requirements.txt", "w") as f: f.write("\n".join(sorted(list(packages_after))) + "\n"); logger.status_ok()
    except IOError: logger.status_fail()

    manifest = read_manifest()
    if not manifest or "dependencies" not in manifest:
        logger.info("No 'project.json' dependencies to update."); return
    
    logger.status_update("Updating project.json")
    removed_count = 0
 
    for pkg_to_remove in packages_to_uninstall:
        normalized_remove_name = pkg_to_remove.lower().replace("_", "-")
        key_found = next((key for key in manifest["dependencies"] if key.lower().replace("_", "-") == normalized_remove_name), None)
        if key_found:
            del manifest["dependencies"][key_found]
            removed_count += 1
            
    if removed_count > 0 and write_manifest(manifest): logger.status_ok()
    elif removed_count == 0: sys.stdout.write(" (package was not a direct dependency)\n")
    else: logger.status_fail()
    
    logger.success("Uninstall and project update complete.")

def handle_uninstall_all():
    """Uninstalls all packages listed in requirements.txt and clears project files."""
    logger.header("Uninstalling ALL Project Dependencies")

    if not os.path.exists("requirements.txt"):
        logger.warning("No 'requirements.txt' file found. Nothing to uninstall.")
        return

    confirmation = logger.prompt(
        "This will uninstall ALL packages listed in requirements.txt. Are you sure? (yes/no):"
    ).strip().lower()

    if confirmation != 'yes':
        logger.info("Operation cancelled by user.")
        return

    if not run_pip_command(["uninstall", "-y", "-r", "requirements.txt"]):
        logger.error("Failed to uninstall all packages. Project files were not changed.")
        sys.exit(1)

    logger.info("Updating dependency files to reflect removal...")

    logger.status_update("Clearing requirements.txt")
    try:
        with open("requirements.txt", "w") as f:
            f.write("# All packages have been uninstalled.\n")
        logger.status_ok()
    except IOError:
        logger.status_fail()

    manifest = read_manifest()
    if manifest and "dependencies" in manifest:
        logger.status_update("Clearing dependencies in project.json")
        manifest["dependencies"] = {}
        if write_manifest(manifest):
            logger.status_ok()
        else:
            logger.status_fail()

    logger.success("Project environment has been cleared successfully.")

def run_initializer():
    """Runs the interactive project setup wizard."""
    display_banner()
    check_environment()
    config = get_project_details()
    manifest_name = create_project_structure(config["name"])
    if config["create_venv"]:
        setup_virtual_env()
    
    full_deps_list, requested_deps_list = install_initial_packages(config["packages"])
    
    create_project_files(config, manifest_name, full_deps_list, requested_deps_list)
    display_summary(config)

def install_initial_packages(packages):
    """
    Installs initial packages and returns two lists:
    1. A complete list of all installed packages for requirements.txt.
    2. A filtered list of just the user-requested packages for project.json.
    """
    if not packages:
        return [], []
        
    logger.header("Installing Initial Dependencies")
    success, _ = run_pip_command(["install"] + packages)
    if not success:
        logger.error("Initial package installation failed. Aborting setup."); sys.exit(1)
        
    all_frozen_packages = sorted(list(get_frozen_packages()))
    
    requested_set = {p.lower().replace("_", "-") for p in packages}
    user_requested_packages = [
        line for line in all_frozen_packages 
        if re.match(r"([^=@\s]+)", line).group(1).lower().replace("_", "-") in requested_set
    ]
    
    return all_frozen_packages, user_requested_packages

def display_banner():
    print(logger._colorize("pinit: The Smart Python Project Initializer", logger.BOLD)); print("-" * 45)

def check_environment():
    current_dir = os.getcwd()
    if not os.access(current_dir, os.W_OK):
        logger.error("The current directory is not writable."); sys.exit(1)
    home_dir = os.path.expanduser('~')
    if os.path.normpath(current_dir) == os.path.normpath(home_dir):
        logger.warning("You are about to initialize a project in your home folder.")
        if logger.prompt("Continue? (yes/no):").strip().lower() != 'yes':
            logger.info("Operation cancelled."); sys.exit(0)

def get_project_details():
    logger.header("Project Configuration")
    while True:
        project_name = logger.prompt("Project name (blank for current dir):").strip() or "."
        if re.search(r'[<>:"/\\|?*]', project_name) is None: break
        logger.warning("Invalid project name. Avoid: / \\ : * ? \" < > |")
    while True:
        main_file = logger.prompt("Main file [main.py]:").strip() or "main.py"
        if not main_file.endswith('.py'): main_file += '.py'
        if '/' not in main_file and '\\' not in main_file: break
        logger.warning("Invalid file name (no paths allowed).")
    create_venv = logger.prompt("Create venv? [Y/n]:").strip().lower() not in ['n', 'no']
    packages = []
    if logger.prompt("Install packages? [Y/n]:").strip().lower() not in ['n', 'no']:
        pkg_str = logger.prompt("Packages (comma-separated):").strip()
        if pkg_str: packages = [p.strip() for p in pkg_str.split(',') if p.strip()]
    return {"name": project_name, "main_file": main_file, "create_venv": create_venv, "packages": packages}

def create_project_structure(project_name):
    logger.header("Creating Project Structure")
    if project_name != ".":
        os.makedirs(project_name, exist_ok=True); os.chdir(project_name)
    logger.success(f"Project initialized in: {os.getcwd()}")
    return os.path.basename(os.getcwd())

def setup_virtual_env():
    logger.header("Setting up Virtual Environment")
    
    logger.status_update("Creating venv")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True, capture_output=True)
        logger.status_ok()
    except subprocess.CalledProcessError as e:
        logger.status_fail()
        logger.error(f"Failed to create virtual environment:\n{e.stderr.decode()}")
        sys.exit(1)

    logger.status_update("Upgrading pip in venv")
    script_dir = "Scripts" if sys.platform == "win32" else "bin"
    venv_python_exe = os.path.join("venv", script_dir, "python.exe" if sys.platform == "win32" else "python")

    if not os.path.exists(venv_python_exe):
        logger.status_fail()
        logger.error("Could not find the Python executable in the newly created venv.")
        sys.exit(1)

    try:
        command = [venv_python_exe, "-m", "pip", "install", "--upgrade", "pip", "-q"]
        subprocess.run(command, check=True, capture_output=True)
        logger.status_ok()
    except subprocess.CalledProcessError as e:
        logger.status_fail()
        logger.warning(f"Failed to upgrade pip, but the venv was created successfully.")
        logger.warning("You may want to activate the venv and run 'pip install --upgrade pip' manually.")

def get_full_dependency_tree(packages):
    """
    Recursively finds all dependencies for a given list of packages.
    Returns a complete set of all packages in the dependency tree.
    """
    to_process = list(packages)
    full_tree = set(packages)
    
    while to_process:
        package = to_process.pop(0)
        dependencies = get_package_dependencies(package)
        for dep in dependencies:
            normalized_dep = dep.lower().replace("_", "-")
            
            is_new = True
            for existing_pkg in full_tree:
                if existing_pkg.lower().replace("_", "-") == normalized_dep:
                    is_new = False
                    break
            
            if is_new:
                full_tree.add(dep)
                to_process.append(dep)
                
    return full_tree

def create_project_files(config, manifest_name, full_deps, requested_deps):
    logger.header("Creating Project Files")
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(full_deps) + "\n")
        
    with open(config["main_file"], "w") as f:
        f.write('def main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n')
        
    dependencies = {p.split('==')[0]: p.split('==')[1] for p in requested_deps if '==' in p}
    
    manifest = {
        "projectName": manifest_name, 
        "version": "0.1.0", 
        "mainFile": config["main_file"],
        "scripts": {
            "dev": f"python {config['main_file']}"
        },
        "dependencies": dependencies
    }
    
    with open("project.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    logger.success(f"Project files created: project.json, requirements.txt, and {config['main_file']}")

def display_summary(config):
    """Displays a final, comprehensive summary with OS-specific instructions."""
    logger.header("Setup Complete")
    print(logger._colorize("\nYour project is ready! Here are the most common commands:", logger.BOLD + logger.YELLOW))

    steps = []

    if config["name"] != ".":
        steps.append(f'Navigate to your project: {logger._colorize(f"cd \"{config["name"]}\"", logger.CYAN)}')

    steps.append(f'Run your default script: {logger._colorize("pinit run dev", logger.CYAN)}')

    if config["create_venv"]:
        steps.append(f'Enter an activated shell (recommended): {logger._colorize("pinit shell", logger.CYAN)}')
        
        if sys.platform == "win32":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        steps.append(f'Or, to activate it manually: {logger._colorize(activate_cmd, logger.CYAN)}')

    steps.extend([
        f'Add a new package: {logger._colorize("pinit install <package>", logger.CYAN)}',
        f'Remove a package: {logger._colorize("pinit uninstall <package>", logger.CYAN)}',
        f'Restore all packages from files: {logger._colorize("pinit install", logger.CYAN)}',
    ])

    for i, step in enumerate(steps, 1):
        print(f" {i}. {step}")

    print() 
    logger.info(
        "This tool automatically uses the 'venv' for commands like `run`, `install`, and `uninstall`."
    )
    logger.info(
        "You only need to activate the shell (using `pinit shell` or manually) for interactive work."
    )

def main():
    try:
        if len(sys.argv) < 2:
            run_initializer(); return

        command = sys.argv[1].lower()
        args = sys.argv[2:]

        if command == 'install':
            if not args:
                handle_install_from_file()
            else:
                handle_install_new_packages(args)
        
        elif command == 'uninstall':
            if not args:
                logger.error("Usage: pinit uninstall <package-name> OR --all"); sys.exit(1)
            
            if '--all' in args or '-all' in args:
                handle_uninstall_all()
            else:
                handle_uninstall_packages(args)
        
        elif command == 'run':
            handle_run_script(args)
        
        elif command == 'shell':
            handle_shell()

        else:
            logger.error(f"Unknown command: '{command}'")
            logger.info("Available commands: install, uninstall, run, shell")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.error("\n\nOperation aborted by user.")
    except Exception as e:
        logger.error(f"\nAn unexpected error occurred: {e}")
if __name__ == "__main__":
    main()