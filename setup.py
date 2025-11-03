# setup.py
"""archiverr kurulum paketi."""
from setuptools import setup, find_packages

with open("README_YML_ENGINE.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="archiverr",
    version="0.2.0",
    description="Gelişmiş medya dosya organizatörü - TMDb + FFprobe + YAML engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="archiverr team",
    author_email="",
    url="https://github.com/yourusername/archiverr",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "archiverr=archiverr.cli.main:run_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
