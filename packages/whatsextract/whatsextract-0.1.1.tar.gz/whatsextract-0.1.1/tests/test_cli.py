import json
import os
import subprocess
import sys

BASE = os.environ.get("WE_BASE_URL", "http://localhost:8080")
KEY = os.environ.get("WE_API_KEY", "we_dev_local_1234567890")

def test_cli_extract():
    cmd = [
        sys.executable, "-m", "whatsextract.cli", "extract",
        "Priya — priya@acme.com +1 415 555 0199"
    ]
    env = {**os.environ, "WE_API_KEY": KEY, "WE_BASE_URL": BASE}
    out = subprocess.check_output(cmd, env=env).decode()
    data = json.loads(out)
    assert data["email"] == "priya@acme.com"
