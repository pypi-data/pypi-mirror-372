# noinspection PyProtectedMember
def register_all():
    from .checkers.flake8_bandit            import __all__
    from .checkers.flake8_bugbear           import __all__
    from .checkers.flake8_class_c           import __all__
    from .checkers.flake8_docstrings        import __all__
    from .checkers.flake8_oneliners         import __all__
    from .checkers.flake8_rst               import __all__
    from .checkers.flake8_string_format     import __all__
    from .checkers.pycodestyle              import __all__
    from .checkers.pyflakes                 import __all__
    from .checkers.wemake_python_styleguide import __all__
