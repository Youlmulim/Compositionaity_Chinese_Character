"""Package metadata for installing the experiment on another device."""

from setuptools import find_namespace_packages, setup


setup(
    name="compositionality-chinese-character",
    version="0.1.0",
    packages=find_namespace_packages(include=["function", "function.*"]),
    include_package_data=True,
    package_data={"function.utils.sounds": ["*.wav"]},
    install_requires=[
        "psychopy",
        "psychtoolbox",
    ],
    python_requires=">=3.11,<3.12",
)
