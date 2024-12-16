import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install

# List of packages that need to be installed first
PREREQS = ["numpy>=1.9"]


def requires(packages):
    """
    Install packages in order using pip.
    """
    python_path = sys.executable
    cmd_template = '"%s" -m pip install %%s' % python_path
    for pkg in packages:
        subprocess.check_call(cmd_template % pkg, shell=True)


class OrderedInstall(install):
    def run(self):
        requires(PREREQS)
        install.run(self)


class OrderedDevelop(develop):
    def run(self):
        requires(PREREQS)
        develop.run(self)


class OrderedEggInfo(egg_info):
    def run(self):
        requires(PREREQS)
        egg_info.run(self)


CMD_CLASSES = {
    "install": OrderedInstall,
    "develop": OrderedDevelop,
    "egg_info": OrderedEggInfo,
}

setup(
    name="thought-miner-alignment",
    version="0.1.0",  # Replace with actual version
    description="forced alignment api (audio+text->synchronization mapping)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Clark Saben",
    author_email="",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click",
        "BeautifulSoup4>=4.5.1",
        "lxml>=3.6.0",
        "numpy>=1.9",  # Even if listed here, it will be installed first by our custom classes
        "aeneas",
    ],
    extras_require={
        "dev": ["ruff", "mypy", "pytest"],
    },
    entry_points={
        "console_scripts": [
            "thought-miner-alignment=thought_miner_alignment.__main__:thought_miner_alignment",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    cmdclass=CMD_CLASSES,
)
