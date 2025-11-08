from setuptools import setup, find_packages

setup(
    name="archiverr",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyyaml>=6.0.1",
        "jinja2>=3.1.2",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "archiverr=archiverr.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
