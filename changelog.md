# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add logging to file. Logging rotated between 5 1mb files.
- Make it possible to load and save arbie state on startup, exit and crash.
- Add CLI option for log path.
- Add CLI option for state save path.
- Add CLI option for state load path.

### Changed

### Removed
- Moved Jupyter examples to [arbie-examples](https://github.com/owodunni/arbie-examples)

## [0.3.0] - The Scraper - 2020-11-02
### Added
- Find all cycles in a set of Pools. These can then be converted to trading opertunities.
- CLI application structure. Making it possible to configure Actions from yaml config.
- Add logging framework. Making it possible to write info to console.
- Add Action for finding Pools from PoolContracts like Uniswap and Balancer.
- Make it possible to specify address to WETH in config.yaml.
- Add functionality making it possible to find all pools and pairs.

## [0.2.0] - The Base - 2020-10-12
### Added
- Smart contract wrapper for interacting with balancer and uniswap.
- Automated market maker modell called Pool. Can be used to simulate Uniswap or balancer.
- TradingGraph functionality built on top of Networkx.
- Ethereum system tests against Geth

### Changed

### Removed
