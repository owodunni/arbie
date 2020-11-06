"""Unittest of __main__.py."""
import pytest
from pytest_mock.plugin import MockerFixture

from Arbie.__main__ import main
from Arbie.Actions import Store


@pytest.fixture
def config_file() -> str:
    return """
    actions:
        PathFinder:
            input:
                unit_of_account: weth
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


class TestMain(object):
    def test_config_not_found(self, mocker: MockerFixture):
        mocker.patch("Arbie.__main__.handlers.RotatingFileHandler")
        mocker.patch("Arbie.__main__.logging.getLogger")
        with pytest.raises(FileNotFoundError):
            main(["-f", "giberich.yml"])

    def test_open_conf_and_load_store(
        self, config_file: str, store: Store, mocker: MockerFixture
    ):
        mocker.patch("Arbie.__main__.handlers.RotatingFileHandler")
        mocker.patch("Arbie.__main__.logging.getLogger")
        mocker.patch("builtins.open", mocker.mock_open(read_data=config_file))
        mocker.patch("Arbie.__main__.path.isfile", return_value=True)
        load_mock = mocker.patch("Arbie.arbie.pickle.load", return_value=store)
        dump_mock = mocker.patch("Arbie.arbie.pickle.dump")
        run_mock = mocker.patch("Arbie.arbie.ActionTree.run")

        main(["-f", "giberich.yml"])
        assert dump_mock.called
        assert load_mock.called
        assert run_mock.called
