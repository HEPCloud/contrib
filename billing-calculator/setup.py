import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bill-calculator-hep-mapsacosta", # Replace with your own username
    version="0.0.2",
    author="Maria P. Acosta F.",
    author_email="macosta@fnal.gov",
    description="Billing calculations and threshold alarms for hybrid cloud setups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hepcloud-git.fnal.gov/macosta/bill-calculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
