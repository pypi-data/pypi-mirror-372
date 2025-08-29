"""Setup file for the Hermes package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the version from the VERSION file
with (Path(__file__).parent.absolute() / "VERSION").open() as version_file:
    version = version_file.read().strip()

long_description: str
with Path("README.md").open() as readme_file:
    long_description = readme_file.read()

setup(
    name="hermes-cai",
    version=version,
    packages=find_packages(include=["hermes_cai", "hermes_cai.*"]),
    include_package_data=True,
    package_data={"hermes_cai": ["templates/*", "contrib/vocab/*"]},
    install_requires=[
        "prompt-poet==0.0.49",
        "prometheus-client==0.20.0",
        "pydantic>=2.7.4",
    ],
    author="James Groeneveld",
    author_email="james@character.ai",
    description="The simplest way of using control flow (like if statements and for loops) to build production-grade prompts for LLMs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/character-tech/chat-stack",
    python_requires=">=3.10",
    license="MIT",
)
