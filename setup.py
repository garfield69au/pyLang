import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyduq",
    version="0.0.4",
    author="Shane J. Downey",
    author_email="shane.downey69au@gmail.com",
    description="A tool to validate data accoridng to the dimensions of data quality.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sjdowney/pyduq",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Freely Distributable",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "plotly",
        "pyodbc",
        "prettytable",
        "dicttoxml",
        "openpyxl"
    ],
    python_requires='>=3.4',
)