"""Unittest of __main__.py."""
import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.__main__ import main
from Arbie.Actions import Store


@pytest.fixture
def config_file() -> str:
    return """
    action_tree:
        actions:
            PathFinder:
                input:
                    weth: weth
                    min_liquidity: 4
                output:
                    cycles: found_cycles
            Arbitrage:
    """


@pytest.fixture
def store() -> Store:
    store = Store()
    store.add("pools", None)
    store.add("weth", None)
    return store


def setup_mocks(mocker, config_file):
    mocker.patch("Arbie.__main__.handlers.RotatingFileHandler")
    mocker.patch("Arbie.__main__.logging.getLogger")
    if config_file is not None:
        mocker.patch("builtins.open", mocker.mock_open(read_data=config_file))


def run_main():
    main(["-f", "giberich.yml"])


class TestMain(object):
    def test_config_not_found(self, mocker: MockerFixture):
        setup_mocks(mocker, None)
        with pytest.raises(FileNotFoundError):
            run_main()

    def test_setup_and_run(self, config_file: str, store: Store, mocker: MockerFixture):
        setup_mocks(mocker, config_file)
        run_mock = mocker.patch("Arbie.settings_parser.ActionTree.run")

        run_main()
        assert run_mock.called

    def test_fail_on_run(self, config_file: str, store: Store, mocker: MockerFixture):
        setup_mocks(mocker, config_file)
        run_mock = mocker.patch("Arbie.settings_parser.ActionTree.run")
        run_mock.side_effect = ValueError("Failed to run action")

        with pytest.raises(ValueError):
            run_main()

    def test_key_not_in_store(self, config_file: str, mocker: MockerFixture):
        setup_mocks(mocker, config_file)

        with pytest.raises(ValueError):
            run_main()
