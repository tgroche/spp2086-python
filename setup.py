import setuptools
import os


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="spp2086",
    version="0.0.1",
    author="Tycho Groche",
    author_email="groche@mv.uni-kl.de",
    description="A collection of utilities created for use in the SPP 2086",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"spp2086": "src/spp2086"},
    packages=setuptools.find_packages(where="src"),
    package_data={
        "spp2086": ["measurement_data/schemas/*.json"]
        },
    python_requires=">=3.6",
    install_requires=[
        "jsonschema >= 4"
    ]
)
