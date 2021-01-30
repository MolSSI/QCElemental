from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--validate", action="store_true", help="validate JSON from previous test run against exported schema"
    )


@pytest.fixture(scope="session", autouse=True)
def set_up_overall(request):
    # in all pytest runs except --validate (which uses the files), clear away the JSON examples and generate fresh
    if not request.config.getoption("--validate", default=False):
        _data_path = Path(__file__).parent.resolve() / "tests" / "qcschema_instances"
        for fl in _data_path.rglob("*.json"):
            fl.unlink()


def pytest_runtest_setup(item):
    # there's a bug where can only set options if specify path in call, so needs to be ``pytest qcelemental/ --validate``

    # skip     the validate-generated-instances-against-exported-schema tests on most ``pytest`` runs.
    # run only the validate-generated-instances-against-exported-schema tests on ``pytest --validate`` runs.
    if not item.config.getoption("--validate", default=False) and item.name.startswith("test_qcschema"):
        pytest.skip("can't run with --validate option")
    elif item.config.getoption("--validate", default=False) and not item.name.startswith("test_qcschema"):
        pytest.skip("need --validate option to run")


# Uncomment below to probe for tests needing `@using_web`

# import socket
#
# class block_network(socket.socket):
#    def __init__(self, *args, **kwargs):
#        raise Exception("Network call blocked")
#
# socket.socket = block_network
