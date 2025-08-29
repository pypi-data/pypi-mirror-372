from extended_setup import ExtendedSetupManager

ExtendedSetupManager('linter_adapters').setup \
(
    short_description = "An adapter which provides categorization & descriptions on popular linters & checkers",
    category = 'tools',
    min_python_version = '3.10',
    classifiers =
    [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Flake8',        
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    entry_points =
    {
        'flake8.report':    [ 'pylint-json = linter_adapters.integrations.formatters.flake8_as_pylint_json:PylintJson' ],
        'console_scripts':  [ 'flake8_as_pylint = linter_adapters.integrations.formatters.flake8_for_pycharm:main' ],
    }
)
