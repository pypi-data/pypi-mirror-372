from .client import Client
from .image_client import ImageClient

__name__ = "zerogpt"
__version__ = "2.0.1b0"  # PEP 440
__unstable_tag__ = "UNSTABLE"
__author__ = "RedPiar"
__license__ = "MIT"
__copyright__ = "Copyright 2025 RedPiar"

def _check_pypi_version():
    import sys
    import json
    import urllib.request
    from packaging import version

    if getattr(sys.modules[__name__], "__unstable_tag__", None):
        print(
            f"\n[NOTICE] You are using an UNSTABLE build of '{__name__}' "
            f"({__version__}). Expect bugs, dragons, and maybe crashes.\n"
        )

    try:
        url = f"https://pypi.org/pypi/{__name__}/json"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.load(response)
            latest_version = data["info"]["version"]

            if version.parse(latest_version) > version.parse(__version__):
                print(
                    f"\n[WARNING] A new version of the '{__name__}' package is available: "
                    f"{latest_version} (you have {__version__})\n"
                    f"Please update the package with the command:\n"
                    f"    pip install -U {__name__}\n"
                )
    except Exception:
        pass

_check_pypi_version()
