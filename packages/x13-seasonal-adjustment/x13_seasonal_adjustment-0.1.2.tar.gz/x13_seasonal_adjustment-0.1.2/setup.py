"""
Setup.py for backwards compatibility.
Please use pyproject.toml for configuration.
"""

from setuptools import setup

# Read the requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = []
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="x13-seasonal-adjustment",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=requirements,
)
