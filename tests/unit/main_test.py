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


def setup_mocks(mocker):
    mocker.patch("Arbie.__main__.handlers.RotatingFileHandler")
    mocker.patch("Arbie.__main__.logging.getLogger")


def run_main():
    main(["-f", "giberich.yml"])


class TestMain(object):
    def test_config_not_found(self, mocker: MockerFixture):
        setup_mocks(mocker)
        with pytest.raises(FileNotFoundError):
            run_main()

    def test_setup_and_run(self, config_file: str, store: Store, mocker: MockerFixture):
        setup_mocks(mocker)
        mocker.patch("builtins.open", mocker.mock_open(read_data=config_file))
        mocker.patch("Arbie.__main__.path.isfile", return_value=True)
        load_mock = mocker.patch("Arbie.arbie.pickle.load", return_value=store)
        dump_mock = mocker.patch("Arbie.arbie.pickle.dump")
        run_mock = mocker.patch("Arbie.arbie.ActionTree.run")

        run_main()
        assert dump_mock.called
        assert load_mock.called
        assert run_mock.called

    def test_fail_on_run(self, config_file: str, store: Store, mocker: MockerFixture):
        setup_mocks(mocker)
        mocker.patch("builtins.open", mocker.mock_open(read_data=config_file))
        mocker.patch("Arbie.__main__.path.isfile", return_value=True)
        load_mock = mocker.patch("Arbie.arbie.pickle.load", return_value=store)
        dump_mock = mocker.patch("Arbie.arbie.pickle.dump")
        run_mock = mocker.patch("Arbie.arbie.ActionTree.run")
        run_mock.side_effect = ValueError("Failed to run action")

        with pytest.raises(ValueError):
            run_main()
        assert not dump_mock.called
        assert load_mock.called

    def test_key_not_in_store(self, config_file: str, mocker: MockerFixture):
        setup_mocks(mocker)
        mocker.patch("builtins.open", mocker.mock_open(read_data=config_file))
        mocker.patch("Arbie.__main__.path.isfile", return_value=False)
        dump_mock = mocker.patch("Arbie.arbie.pickle.dump")

        with pytest.raises(ValueError):
            run_main()
        assert not dump_mock.called
