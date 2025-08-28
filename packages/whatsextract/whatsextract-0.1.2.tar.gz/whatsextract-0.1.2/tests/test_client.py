import os
import pytest
from whatsextract import WhatsExtract

BASE = os.environ.get("WE_BASE_URL", "http://localhost:8080")
KEY = os.environ.get("WE_API_KEY", "we_dev_local_1234567890")

def test_extract_smoke():
    c = WhatsExtract(api_key=KEY, base_url=BASE)
    r = c.extract("Priya — priya@acme.com +1 415 555 0199")
    assert r.email == "priya@acme.com"
    assert r.phone.startswith("+1")

@pytest.mark.integration
def test_usage_ok():
    c = WhatsExtract(api_key=KEY, base_url=BASE)
    u = c.get_usage()
    assert "usage" in u
