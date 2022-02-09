import setuptools
import os


#enumerate all files
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files(os.path.join('src', 'measurement_data', 'schemas'))


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
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"": extra_files},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "jsonschema >= 4"
    ]
)
