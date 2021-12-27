"""Adapted from https://github.com/pypa/sampleproject/blob/master/setup.py."""

from setuptools import find_packages, setup

setup(
    # Name of the project.
    name="clothing-rater",
    # Project version.
    version="1.0.0",
    python_requires="==3.8.10",
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description="Clothing Rater",
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    # packages=find_packages(exclude=["contrib", "docs"]),
    packages=find_packages(include=["src"]),
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    #
    install_requires=[
        "google-cloud-vision==2.3.2",
        "fastapi==0.63.0",
        "pydantic==1.8.1",
        # "python-Levenshtein==0.12.0",
        "numpy==1.18.0",
        "nltk==3.5",
        "sqlalchemy==1.4.3",
        "psycopg2-binary==2.8.6",
        "google-cloud-secret-manager==2.3.0",
        "pandas==1.3.2",
        "uvicorn==0.15.0",
        "clothing-rater-database-api @ git+ssh://git@github.com/yohskua/clothing-rater-database-api.git#egg=database",
        "Pillow==8.4.0",
        "python-magic-bin==0.4.14",
        "pyheif==0.6.1",
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install project[tests]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    # extras_require={"tests": ["pylint"]},
    # extra data
    # package_data = {'cvideos':['params/*']},
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # The following will provide a command called `adh-query` which
    # executes the function `main` from this package when invoked:
    # entry_points={"console_scripts": ["mov-encoder=mov-encoder.app:main"]},
)
