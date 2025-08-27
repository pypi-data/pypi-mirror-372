from setuptools import setup, find_packages
import os
import codecs

VERSION = '0.1.0'
DESCRIPTION = "A Python package to load and manage Google Sheets, Excel files, or any spreadsheet data from URLs and file paths."
LONG_DESCRIPTION = ""

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    LONG_DESCRIPTION = "\n" + fh.read()

# Setting up
setup(
    name="sheetsmanager",
    version=VERSION,
    author="Yan Sido",
    author_email="yansido1@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas==2.2.3'],
    keywords=['python', 'google-sheets', 'excel', 'spreadsheet', 'spreadsheet manager', 'sheets manager', 'google sheets loader', 'excel loader'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
