import os
from setuptools import setup, find_packages, Command


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.egg-info")


description = """
demo for tahweela with stochastic trading
"""

setup(
    name="tahweela",
    version="0.1",
    author="mohab metwally",
    author_email="mohab-metwally@riseup.net",
    description=description,
    license="Copyright (c) mohab metwally 2021",
    packages=find_packages(),
    long_description=read("README.md"),
    cmdclass={
        'clean': CleanCommand,
    }
)
