def pytest_addoption(parser):
    parser.addoption('--web3_server', action='store', default='http://127.0.0.1:7545')
