import importlib.metadata

import requests


def check_latest_version(package_name="aipmodel", auto_warn=True):
    try:
        current_version = importlib.metadata.version(package_name)
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        latest_version = response.json()["info"]["version"]
        if current_version != latest_version:
            if auto_warn:
                print(f"[Update] A newer version ({latest_version}) is available. You are using {current_version}.")
            return False, current_version, latest_version
        return True, current_version, latest_version
    except Exception:
        return None, None, None
