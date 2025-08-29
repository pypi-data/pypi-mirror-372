# Python Linter Adapters
Provides bridges for different linters & checkers, mostly [Flake8] plugins,
as well as some bridges for Flake8 as [Pylint].

### Features
* A re-implementation of [flake8-for-pycharm] package:
  + `pylint-json` Flake8 formatter -- emulates Pylint behaviour as a Flake8 formatter
  + `flake8_as_pylint` -- emulates (partially) Pylint CLI with the Flake8 backend
* An API for providing categories & severities for the popular Flake8 plugins:
  + All bundled plugins from the Flake8 base package
  + [flake8-bandit](https://pypi.org/project/flake8-bandit/)
  + [flake8-broken-line](https://pypi.org/project/flake8-broken-line/)
  + [flake8-bugbear](https://pypi.org/project/flake8-bugbear/)
  + [flake8-commas](https://pypi.org/project/flake8-commas/)
  + [flake8-comprehensions](https://pypi.org/project/flake8-comprehensions/)
  + [flake8-datetimez](https://pypi.org/project/flake8-datetimez/)
  + [flake8-debugger](https://pypi.org/project/flake8-debugger/)
  + [flake8-docstrings](https://pypi.org/project/flake8-docstrings/)
  + [flake8-eradicate](https://pypi.org/project/flake8-eradicate/)
  + [flake8-isort](https://pypi.org/project/flake8-isort/)
  + [flake8-quotes](https://pypi.org/project/flake8-quotes/)
  + [flake8-rst-docstrings](https://pypi.org/project/flake8-rst-docstrings/)
  + [flake8-string-format](https://pypi.org/project/flake8-string-format/)
  + [wemake-python-styleguide](https://pypi.org/project/wemake-python-styleguide/)

### PyCharm Integration
This package is inspired by [flake8-for-pycharm] which adapts Flake8 output as Pylint's JSON output.
The original project stopped to work by now due to changes in Flake8 formatters API (or has it ever worked?).

To setup PyCharm integration:

1. Install [Pylint Plugin]
2. In the Settings, select `flake8_as_pylint` executable instead of `pylint` executable:
   ![pycharm-pylint-settings.png](docs/img/pycharm-pylint-settings.png "select '<venv>/Scripts/flake8_as_pylint.exe' here")
3. Any extra parameters would be passed directly to Flake8.
   The only exceptions are:
   + `--output-format/-f` -- passed by PyCharm. Would conflict with `--format`. Supports only `text` and `json`
   + `--help-msg` -- works as in Pylint -- shows info for the specified error codes
   + `--flake8-main/-F` -- new parameter, can be used to override Flake8's main function. Uses Python [EntryPoint] format

The results:
![pycharm-pylint-window.png](docs/img/pycharm-pylint-window.png "PyCharm's Pylint window")
![pycharm-editor-violations.png](docs/img/pycharm-editor-violations.png "Violations in the PyCharm's editor")

// Yes, I am not using those for the personal projects. Have plans to set up my own code style rules.

[flake8]: https://flake8.pycqa.org/en/latest/index.html
[pylint]: https://pylint.readthedocs.io/en/latest/
[flake8-for-pycharm]: https://pypi.org/project/flake8-for-pycharm/
[pylint plugin]: https://plugins.jetbrains.com/plugin/11084-pylint
[EntryPoint]: https://docs.python.org/3.12/library/importlib.metadata.html#importlib.metadata.EntryPoint
