import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "radius: Tests, die radtest/eapol_test und privilegiertes Netzwerk benoetigen.",
    )


def pytest_collection_modifyitems(config, items):
    if os.environ.get("SKIP_RADIUS_TESTS", "0") != "1":
        return
    skip_radius = pytest.mark.skip(
        reason="RADIUS/EAPOL-Tests uebersprungen (SKIP_RADIUS_TESTS=1)"
    )
    for item in items:
        if "radius" in item.keywords:
            item.add_marker(skip_radius)
