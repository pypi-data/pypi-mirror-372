from setuptools import setup, find_packages

setup(
    name                          = "baisstools",  # Unique name on PyPI
    version                       = "0.0.4",
    packages                      = find_packages(),
    install_requires              = [],  # Dependencies (e.g., ["requests", "numpy"])
    author                        = "Abdelmathin Habachi",
    author_email                  = "abdelmathinhabachi@gmail.com" ,
    description                   = "Baiss-Tools is a Python package designed to simplify and enhance the development.",
    long_description              = open("baisstools/README.md").read(),
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/tbeninnovation-mobileapp/baisstools",
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
