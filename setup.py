import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piLang-garfield69au",
    version="0.0.1",
    author="Shane Downey",
    author_email="shane.downey69au@gmail.com",
    description="A tool to validate data accoridng to the dimensions of data quality.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/garfield69au/pyLang",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)