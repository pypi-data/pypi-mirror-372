# Inmanta dev dependencies

This repository create a virtual package that collects and freezes dependencies used to develop inmanta modules and extensions. The default package mainly packages flake8 packages to enfore the inmanta formatting guideliness.

There are a number of optional packages, available in a number of groups:

- modules: All packages required for linting and tests for inmanta modules
- extension: All packages required for linting and tests of inmanta orchestrator extensions
- async: Extra pytest packages for running async tests
- pytest: A curated list of pytest extensions to improve testing and to improve pytest output. 