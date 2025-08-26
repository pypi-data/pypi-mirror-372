import importlib.metadata as metadata
import urllib.request
import urllib.error
import json
import subprocess
import sys
import os
import re
import time

# --- Saved Parameters ---

ENV_FILE = os.path.join(os.path.expanduser("~"), ".tsbuddy_settings")

def load_env_file():
    """Load key-value pairs from .env into os.environ"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, sep, value = line.strip().partition("=")
                    if sep:  # Only set if '=' was found
                        os.environ[key] = value  # override to allow updates


def set_env_variable(key, value):
    """Set or update a key=value in .env file."""
    lines = []
    found = False
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{key}={value}\n")
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)

# Load .env into environment
load_env_file()

# --- Version Handling Functions ---

def get_installed_version(package_name):
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None

def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.load(resp)["info"]["version"]
    except Exception as e:
        print(f"Error fetching latest version for '{package_name}': {e}")
        return None

def get_pypi_description(package_name, limit=3):
    """Fetch the package description from PyPI JSON API."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.load(resp)
            content = data["info"].get("description")
    except Exception as e:
        print(f"Error fetching description for '{package_name}': {e}")
        return None
    
    # Extract the full changelog section
    match = re.search(r"##\s*Changelog\s*([\s\S]*?)(?:\n## |\Z)", content, re.IGNORECASE)
    if not match:
        return None

    changelog_section = match.group(1).strip()

    # Split by full changelog entries (keep the delimiter)
    entries = re.findall(r"(###\s.*?)(?=\n### |\Z)", changelog_section, re.DOTALL)
    
    if not entries:
        return None

    # Take the most recent N entries
    latest_entries = entries[:limit]
    return "\n\n".join(entry.strip() for entry in latest_entries)

# --- Changelog Fetching Function ---

def fetch_changelog(limit=3):
    changelog_url = "https://raw.githubusercontent.com/bgbyte/tsbuddy/main/README.md"
    try:
        with urllib.request.urlopen(changelog_url) as resp:
            content = resp.read().decode("utf‑8")
    except urllib.error.HTTPError as e:
        print(f"Error retrieving changelog: {e}")
        return None

    # Extract the full changelog section
    match = re.search(r"##\s*Changelog\s*([\s\S]*?)(?:\n## |\Z)", content, re.IGNORECASE)
    if not match:
        return None

    changelog_section = match.group(1).strip()

    # Split by full changelog entries (keep the delimiter)
    entries = re.findall(r"(###\s.*?)(?=\n### |\Z)", changelog_section, re.DOTALL)
    
    if not entries:
        return None

    # Take the most recent N entries
    latest_entries = entries[:limit]
    return "\n\n".join(entry.strip() for entry in latest_entries)



# --- Update Function ---

def update_package(package_name):
    print(f"\n🔄 Updating '{package_name}'...\n")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
    print(f"\n✅ '{package_name}' updated.\n")

def update_package_safe(package_name, current_version=None):
    import subprocess, sys, os
    import tempfile

    # Path to re-launch after upgrade
    #relaunch_cmd = [sys.executable, "-m", "tsbuddy"]
    #relaunch_cmd = ["tsbuddy"]
    
    # Path to the temporary updater script
    updater_path = os.path.join(tempfile.gettempdir(), "_tsbuddy_updater.py")

    print(f"\n🔄 Preparing to update '{package_name}'...")

    # Write a temporary updater script
    updater_script = f"""
import time
import subprocess
import sys

print("Waiting for current process to exit...")
time.sleep(2)  # Give time for the main script to exit

subprocess.check_call([r"{sys.executable}", "-m", "pip", "install", "--upgrade", "{package_name}", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org"])
print("\\n"+("#"*15))
print("Please report any bugs to Brian.")
print("If there is an issue, you can revert to your previous version using: ")
print("`pip install tsbuddy=={current_version}`")
print("#"*15,"\\n")
time.sleep(5)
print("\\n* Upgrade complete. You can now rerun tsbuddy.")
"""

    #updater_path = os.path.join(os.getcwd(), "_tsbuddy_updater.py")

    with open(updater_path, "w") as f:
        f.write(updater_script)

    # Launch the updater in a new process
    subprocess.Popen([sys.executable, updater_path], close_fds=True)

    if current_version:
        set_env_variable("TSBUDDY_PREVIOUS_VERSION", current_version)
    print("Exiting to allow upgrade to complete...")
    sys.exit(0)

def downgrade_package_safe(package_name, previous_version):
    import subprocess, sys, os
    import tempfile

    # Path to re-launch after upgrade
    #relaunch_cmd = [sys.executable, "-m", "tsbuddy"]
    #relaunch_cmd = ["tsbuddy"]
    
    # Path to the temporary updater script
    updater_path = os.path.join(tempfile.gettempdir(), "_tsbuddy_updater.py")

    print(f"\n🔄 Preparing to downgrade '{package_name}'...")

    # Write a temporary updater script
    updater_script = f"""
import time
import subprocess
import sys

print("Waiting for current process to exit...")
time.sleep(2)  # Give time for the main script to exit

subprocess.check_call([r"{sys.executable}", "-m", "pip", "install", "{package_name}=={previous_version}", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org"])
print("\\n"+("#"*15))
print("Important: Please report any bugs to Brian.")
print("#"*15,"\\n")
time.sleep(5)
print("\\n* Downgrade complete. You can now rerun tsbuddy.")
"""

    #updater_path = os.path.join(os.getcwd(), "_tsbuddy_updater.py")

    with open(updater_path, "w") as f:
        f.write(updater_script)

    # Launch the updater in a new process
    subprocess.Popen([sys.executable, updater_path], close_fds=True)

    print("Exiting to allow downgrade to complete...")
    sys.exit(0)

def downgrade_to_previous_version(package="tsbuddy"):
    """
    Downgrade tsbuddy to the previous version found in the environment variable TSBUDDY_PREVIOUS_VERSION.
    """
    previous_version = os.environ.get("TSBUDDY_PREVIOUS_VERSION")
    if not previous_version:
        print("No previous version found in environment variable TSBUDDY_PREVIOUS_VERSION loaded from ~/.tsbuddy_settings")
        print("If you want to downgrade, please specify the version manually, e.g.: 0.0.23")
        #print("pip install tsbuddy==0.0.23")
        previous_version = input("Enter the version to downgrade to: ").strip()
        if not previous_version:
            return
    print(f"Enter version to downgrade to. By default, previous version: {previous_version}")
    previous_version = input(f"Downgrade to version [{previous_version}]: ").strip() or previous_version
    print(f"\n⏬ Downgrading 'tsbuddy' to previous version: {previous_version} ...\n")
    try:
        downgrade_package_safe(package, previous_version)
        print(f"\n✅ 'tsbuddy' downgraded to version {previous_version}.")
        #set_env_variable("TSBUDDY_IGNORE_VERSION", "")  # Clear ignore version if set
    except Exception as e:
        print(f"Error downgrading to version {previous_version}: {e}")

def choice_form():
    choice = input("Do you want to upgrade or downgrade? [U/d]: ").strip().lower()
    if choice == 'u':
        update_package_safe("tsbuddy", current_version=get_installed_version("tsbuddy"))
    elif choice == 'd':
        downgrade_to_previous_version()
    else:
        return None


# --- Main Logic ---

def main():
    package = "tsbuddy"
    #print(f"\nChecking '{package}'...\n")

    current_version = get_installed_version(package)
    latest_version = get_latest_version(package)

    if latest_version is None:
        print(f"⚠ Could not determine the latest version of '{package}'.")
        return

    # Check if user wants to ignore this version
    ignore_version = os.environ.get("TSBUDDY_IGNORE_VERSION")
    if latest_version == ignore_version != current_version:
        print(f"⚠  Old version {current_version}\n⬆️ Upgrade {package} to {latest_version} manually using: \npip cache purge\npip install --upgrade {package}")
        time.sleep(1)
        return

    show_changelog = False

    if current_version is None:
        print(f"📦 '{package}' is not installed. Latest available: {latest_version}")
        show_changelog = True
    elif current_version != latest_version:
        show_changelog = True
    else:
        print(f"✅ '{package}' is up to date ({current_version})")
        return

    # Show changelog if available
    if show_changelog:
        # print("\n--- 📦 PyPI Description ---\n")
        # description = get_pypi_description(package)
        # if description:
        #     print(description)
        # else:
        #     print("No description found on PyPI.")
        print("\n--- 📄 Latest Changelog Entries ---\n")
        #changelog = fetch_changelog(limit=3)
        changelog = get_pypi_description(package)
        if changelog:
            print(changelog)
            print("\nView full history at: https://github.com/bgbyte/tsbuddy#changelog")
            print(f"\n⬇ A newer version of '{package}' is available: {current_version} → {latest_version}")
        else:
            print("No changelog found.")

    # Ask for update
    confirm = input(f"Do you want to update '{package}' to {latest_version}? [y/N], 'N' will skip future prompts for {latest_version}: ").strip().lower()
    if confirm == 'y':
        update_package_safe(package, current_version)
    else:
        set_env_variable("TSBUDDY_IGNORE_VERSION", latest_version)
        print(f"Skipping version {latest_version}.")
        print("If you want to update before the next release, run `pip install --upgrade tsbuddy` manually.")
        print("Loading tsbuddy...")
        time.sleep(1)

if __name__ == "__main__":
    main()
