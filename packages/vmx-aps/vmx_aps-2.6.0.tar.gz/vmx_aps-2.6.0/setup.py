import setuptools
from pathlib import Path

# Read description.md content
this_directory = Path(__file__).parent
long_description = (this_directory / "description.md").read_text(encoding="utf-8")

setuptools.setup(
    name="vmx-aps",
    version="2.6.0",
    author="Verimatrix Inc.",
    author_email="blackhole@verimatrix.com",
    description="APS command line wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-dateutil",
        "requests",
        "pyaxmlparser",
        "backoff",
        "coloredlogs"
    ],
    entry_points={
        "console_scripts": [
            "vmx-aps=apsapi.aps:main",
        ],
    },
)
