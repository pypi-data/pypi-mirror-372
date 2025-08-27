import paramiko
from getpass import getpass
import time
import re
import json
import os
import sys
import subprocess

image_map = {
    "nandi_sim": ["Nossim.img"],
    "everest": ["Uos.img"],
    "medora_sim64": ["Mossim.img", "Menisim.img"],
    "tor": ["Tos.img"],
    "vindhya": ["Nos.img"],
    "medora": ["Mos.img", "Meni.img", "Mhost.img"],
    "yukon": ["Yos.img"],
    "shasta": ["Uos.img"],
    "aravalli": ["Nosa.img"],
    "shasta_n": ["Uosn.img"],
    "whitney": ["Wos.img"],
    "nandi": ["Nos.img"],
    "whitney_sim": ["Wossim.img"],
    "kailash": ["Kaos.img"]
}

model_family_map = {
 '6360': 'aravalli',
 '6465': 'vindhya',
 '6560': 'nandi',
 '6570M': 'whitney',
 '6860': 'shasta',
 '6860N': 'shasta_n',
 '6865': 'everest',
 '6870': 'kailash',
 '6900 Tor': 'tor',
 '6900 Yukon': 'yukon',
 '9900': 'medora'
 }

model_6900_variants = {
    "6900 Yukon":"T48C6/V72/V48C8/X48C6", 
    "6900 Tor":"X20/X40/X72/T20/T40/Q32"
    }

family_model_image_map = {
  "everest": {
    "models": ["6865", "6865"],
    "Img": "Uos.img"
  },
  "tor": {
    "models": ["6900 Tor", "X20/X40/X72/T20/T40/Q32"],
    "Img": "Tos.img"
  },
  "vindhya": {
    "models": ["6465", "6465"],
    "Img": "Nos.img"
  },
  "medora": {
    "models": ["9900", "9900"],
    "Img": "Mos.img"
  },
  "yukon": {
    "models": ["6900 Yukon", "T48C6/V72/V48C8"],
    "Img": "Yos.img"
  },
  "shasta": {
    "models": ["6860", "6860"],
    "Img": "Uos.img"
  },
  "aravalli": {
    "models": ["6360", "6360"],
    "Img": "Nosa.img"
  },
  "shasta_n": {
    "models": ["6860N", "6860N"],
    "Img": "Uosn.img"
  },
  "whitney": {
    "models": ["6570M", "6570M"],
    "Img": "Wos.img"
  },
  "nandi": {
    "models": ["6560", "6560"],
    "Img": "Nos.img"
  },
  "kailash": {
    "models": ["6870", "6870"],
    "Img": "Kaos.img"
  }
}

def safe_password_prompt(prompt="Password: ", fallback="switch"):
    try:
        if sys.stdin.isatty():
            return getpass.getpass(prompt) or fallback
        else:
            # Try manual stty fallback
            try:
                print("Incompatible terminal detected. Password will not be hidden.\n")
                sys.stdout.write(prompt)
                sys.stdout.flush()
                subprocess.check_call(["stty", "-echo"])
                password = input("")
            finally:
                subprocess.call(["stty", "echo"])
                sys.stdout.write("\n")
            return password or fallback
    except Exception:
        # Final fallback
        #print("Falling back to visible input.")
        return input(prompt) or fallback

# Load GA index once at the module level
ga_index_path = os.path.join(os.path.dirname(__file__), "ga_index.json")
with open(ga_index_path) as f:
    ga_index = json.load(f)

def wait_for_shell(shell, timeout=120):
    """Read output from shell until timeout or prompt returns."""
    shell.settimeout(2)
    output = ""
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = shell.recv(4096).decode("utf-8")
            output += chunk
            # Break if we detect shell prompt (e.g., ending in # or $)
            if any(p in chunk for p in ["# ", "#->", "$ ", ">", "login: "]):
                break
        except Exception:
            time.sleep(1)
    return output

def prompt_initial_aos_version():
    """Prompts the user for the full AOS version string."""
    return input("\nEnter AOS version string (e.g., 8.9.221.R03): ").strip()

def parse_aos_version_string(version_string):
    """
    Parses the AOS version string into major, build, and release components.
    Returns a dictionary with 'major', 'build', and 'release' keys.
    Values can be None if not found in the string.
    """
    regex_pattern = r'^(\d+\.\d+)(?:\.(\d+))?(?:\.?([Rr]\d+))?$'
    match = re.match(regex_pattern, version_string)

    if match:
        major = match.group(1)
        build = match.group(2) if match.group(2) else None  # Can be None
        release_raw = match.group(3).upper() if match.group(3) else None # Can be None
        # Conditional formatting
        release = None
        if release_raw:
            if major.startswith("8."):
                # Convert to "R03" format
                number_part = release_raw[1:].zfill(2)  # Pad to 2 digits
                release = "R" + number_part
            else:
                release = release_raw
        return {"major": major, "build": build, "release": release}
    else:
        # If the basic major.minor pattern isn't found, return None for all
        return {"major": None, "build": None, "release": None}

def validate_and_complete_version_parts(parsed_parts):
    """
    Validates parsed version sections. If a section (build or release)
    is missing (None), prompts the user for it.
    Assumes 'major' will always be present if initial parsing was somewhat successful.
    """
    major = parsed_parts.get("major") # Should already be there from a successful parse
    build = parsed_parts.get("build")
    release = parsed_parts.get("release")
    if major is None:
        # This indicates a fundamental failure in parsing the initial string.
        # The main loop should handle this by re-prompting for the full string.
        # However, if we wanted to be extremely robust and prompt for major here:
        while not major:
            major = input("Enter AOS Major version (e.g., 8.9): ").strip()
        # For this exercise, we assume parse_aos_version_string got the major if input was valid.
        #pass # Major should be handled by the calling function based on parse_aos_version_string output
    if build is None:
        build = input("Enter AOS Build Number (e.g., 221): ").strip() or "221" # Default if empty
    if release is None:
        release = input("Enter AOS Release (e.g., R03): ").strip() or "R03" # Default if empty
    return {"major": major, "build": build, "release": release}

def get_aos_version_orchestrator():
    """Orchestrates prompting, parsing, and validation to get the full AOS version."""
    while True:
        initial_version_string = prompt_initial_aos_version()
        parsed_components = parse_aos_version_string(initial_version_string)
        if not parsed_components.get("major"):
            print("Invalid format. Major version (e.g., X.Y) could not be parsed. Please try again.")
            continue # Re-prompt for the full string
        # Now, parsed_components["major"] is guaranteed to be something.
        # Fill in any missing optional parts (build, release)
        completed_components = validate_and_complete_version_parts(parsed_components)
        aos_major = completed_components["major"]
        aos_build = completed_components["build"]
        aos_release = completed_components["release"]
        full_version = f"{aos_major}.{aos_build}.{aos_release}"
        confirm = input(f"Confirm full AOS version string [{full_version}] [y]/n: ").strip().lower() or "y"
        if confirm == "y":
            return aos_major, aos_build, aos_release
        # If not 'y', the loop will restart, prompting for the initial string again.

def get_aos_version_simple():
    while True:
        """Prompts for AOS version components and confirms the full version."""
        aos_major = input("Enter AOS Major Version (e.g., 8.9) [8.9]: ") or "8.9"
        aos_build = input("Enter AOS Build Number (e.g., 221) [221]: ") or "221"
        aos_release = input("Enter AOS Release (e.g., R03) [R03]: ") or "R03"
        full_version = f"{aos_major}.{aos_build}.{aos_release}"
        confirm = input(f"Confirm full AOS version string [{full_version}] [y]/n: ").strip().lower() or "y"
        if confirm == "y":
            return aos_major, aos_build, aos_release
        # If not 'y', the loop will restart, prompting for the initial string again.

def get_ga_build(version, family):
    try:
        build = ga_index[version][family]
        if build in ('', 'N/S', 'N/A', 'UNK'):
            raise ValueError(f"No GA build available for version {version} and family {family}. Build returned: {build}")
        return build
    except KeyError:
        raise ValueError(f"No GA build found for version {version} and family {family}")

def lookup_ga_build():
    """Allows the user to look up GA builds with an option to upgrade OmniSwitch."""
    print("\n----- Models -----")
    print("---- Model : Family ----")
    for model, family in model_family_map.items():
        max_key_length = max(len(k) for k in model_family_map)
        print(f"{model:<{max_key_length}} : {family}")
    print("\n----- 6900 Variants -----")
    print("-- Variant : Models --")
    for model, variants in model_6900_variants.items():
        max_key_length = max(len(k) for k in model_6900_variants)
        print(f"{model:<{max_key_length}} : {variants}")
    print("\nLookup the GA build by providing a model or device IP...")
    while True:
        user_input = input("Enter a model name (e.g., 6900 Yukon) or device IP (e.g., 192.168.1.1) [exit]: ").strip()
        if not user_input or user_input.lower() == 'exit':
            print("Canceling GA build lookup...")
            break
        # Use regex to check for IP (contains . or :)
        if re.search(r'[.:]', user_input):
            # Assume IP, prompt for credentials
            ip = user_input
            username = input(f"Enter username for {ip} [admin]: ") or "admin"
            password = getpass(f"Enter password for {ip} [switch]: ") or "switch"
            host = {"ip": ip, "username": username, "password": password}
            family = get_family_from_ip(host)
            if not family:
                print(f"Could not determine family from IP {ip}.")
                continue
            print(f"Family for {ip}: {family}")
        else:
            # Assume model
            model = user_input
            family = model_family_map.get(model)
            if not family:
                print(f"Unknown model: {model}. Please try again.")
                continue
            print(f"Family for model {model}: {family}")
        ga_prompt_ver = input("Provide the AOS version & Release for GA lookup (e.g., 8.10R02) [exit]: ").strip().upper() or None
        if not ga_prompt_ver or ga_prompt_ver.lower() == 'exit':
            print("Lookup canceled.")
            continue
        gadl = input(f"Would you like to download to OmniSwitch? [y]/n: ").strip().lower() or "y"
        try:
            ga_ver, ga_release = ga_prompt_ver.split('R') if ga_prompt_ver else (None, None)
            ga_release = "R" + ga_release  # Add "R" to the beginning of the ga_release string
            found_ga_build = f"{ga_ver}{get_ga_build(ga_prompt_ver, family)}.{ga_release}"
            print("GA Build: ", found_ga_build)
            if gadl == "y":
                aosup(found_ga_build=found_ga_build)
        except Exception as e:
            print(f"Error looking up GA build: {e}")

def collect_hosts():
    """Collects device details from the user and returns a list of hosts."""
    hosts = []
    print("\nEnter device details. Press Enter without an IP to finish.")
    while True:
        ip = input("Enter device IP: ").strip()
        if not ip:
            break
        username = input(f"Enter username for {ip} [admin]: ") or "admin"
        password = safe_password_prompt(f"Enter password for {ip} [switch]: ")
        #password = getpass(f"Enter password for {ip} [switch]: ") or "switch"
        hosts.append({"ip": ip, "username": username, "password": password})
    return hosts


def get_platform_family(shell):
    """Extracts the platform family from the shell prompt."""
    shell.send("echo $PS1\n")
    time.sleep(1)
    output = shell.recv(2048).decode("utf-8")
    lines = output.strip().splitlines()
    ps1 = lines[-1] if lines else ""
    family = ps1.split()[0].lower() if ps1 else None
    return family


def aosup(found_ga_build=None):
    """Prompt the user for folder name and reload option, then execute main with those arguments."""
    folder_name = input("Which folder name would you like to download to? [working]: ").strip() or "working"
    reload_choice = input("Would you like to reload when finished? [y]/n: ").strip().lower() or "y"
    reload_when_finished = reload_choice == "y"
    main(folder_name=folder_name, reload_when_finished=reload_when_finished, found_ga_build=found_ga_build)
    #if reload_when_finished:
    #    print(f"Reloading from folder '/flash/{folder_name}'...")
    #else:
    #    print(f"Download completed. Files are in the '/flash/{folder_name}' directory.")
    #return folder_name, reload_when_finished


def download_images_for_host(host, aos_major, aos_build, aos_release, image_map, base_ip, base_dir, folder_name=None, reload_when_finished=False):
    ip = host["ip"]
    print(f"\nConnecting to {ip}...")
    try:
        # Connect via SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=host["username"], password=host["password"], timeout=10)
        shell = client.invoke_shell()
        shell.send("su\n")
        time.sleep(1)
        shell.recv(1024)  # No password needed
        family = get_platform_family(shell)
        if not family or family not in image_map:
            print(f"[{ip}] Unknown or missing platform family: '{family}'")
            client.close()
            return
        print(f"[{ip}] Platform family: {family}")
        images = image_map[family]
        aos_major_fmt = aos_major.replace('.', '_')
        image_path = f"{base_dir}/OS_{aos_major_fmt}_{aos_build}_{aos_release}/{family}/Release/"
        for img in images:
            url = f"{base_ip}{image_path}{img}"
            if folder_name:
                cmd = f"curl -kL \"{url}\" --output /flash/{folder_name}/{img}"
                shell.send(cmd + "\n")
                print(f"[{ip}] Downloading {img}...")
                download_output = wait_for_shell(shell)
                print(f"[{ip}] Downloaded {img} to /flash/{folder_name}/")
            else:
                cmd = f"curl -kL \"{url}\" --output /flash/{img}"
                shell.send(cmd + "\n")
                print(f"[{ip}] Downloading {img}...")
                download_output = wait_for_shell(shell)
                print(f"[{ip}] Downloaded {img} to /flash/")
        if reload_when_finished and folder_name:
            shell.send("exit\n")
            time.sleep(4)
            shell.send(f"echo 'y' | reload from {folder_name} no rollback-timeout\n")
            time.sleep(4)
            print(f"[{ip}] Started reload from /flash/{folder_name}/")
        client.close()
    except Exception as e:
        print(f"[{ip}] ERROR: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def get_family_from_filename(filename: str) -> str | None:
    """Infers the family by finding the provided filename in the mapping."""
    for family, filenames_list in image_map.items():
        if filename in filenames_list:
            return family
    return None

def get_filenames_for_family(family: str) -> list[str] | None:
    """Retrieves the list of software filenames for a given family."""
    return image_map.get(family)

def get_family_from_ip(host: str) -> str | None:
    """
    Connects to a device via SSH to determine its model and then its family.
    """
    ip = host["ip"]
    print(f"\nConnecting to {ip}...")
    try:
        # Connect via SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=host["username"], password=host["password"], timeout=10)
        shell = client.invoke_shell()
        shell.send("su\n")
        time.sleep(1)
        shell.recv(1024)  # No password needed
        family = get_platform_family(shell)
        if not family or family not in image_map:
            print(f"[{ip}] Unknown or missing platform family: '{family}'")
            client.close()
            return
        print(f"[{ip}] Platform family: {family}")
        client.close()
        return family
    except Exception as e:
        print(f"[{ip}] ERROR: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def main(folder_name=None, reload_when_finished=False, found_ga_build=None):
    print("\nNote: you can lookup the GA build with aosdl-ga CLI command.\n")
    if not found_ga_build:
        aos_major, aos_build, aos_release = get_aos_version_simple()
    else:
        parts = found_ga_build.split('.')
        aos_major, aos_build, aos_release = [".".join(parts[:2]), parts[2], parts[3]]
    print(f"Using AOS Version: {aos_major}.{aos_build}.{aos_release}")
    # Image mapping, moved to global scope for reusability
    base_ip = "http://10.46.4.37"
    base_dir = "/bop/images"
    hosts = collect_hosts()
    for host in hosts:
        download_images_for_host(host, aos_major, aos_build, aos_release, image_map, base_ip, base_dir, folder_name, reload_when_finished)

if __name__ == "__main__":
    main()

