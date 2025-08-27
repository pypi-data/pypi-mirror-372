from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt if it exists
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="israeli-law-amender",
    version="1.0.2",
    author="Hila Peled, Nitzan Naimi, Ohad Nahari, Ran Cohen",
    author_email="hila.peled@mail.huji.ac.il, nitzan.naimi@mail.huji.ac.il, ohad.nahar@mail.huji.ac.il, ran.cohen@mail.huji.ac.il",
    description="A Python package for processing and amending Israeli laws using AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Double-N-A/israeli-law-amender",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "amend-law=israeli_law_amender.core:main",
        ],
    },
    include_package_data=True,
    package_data={
        "israeli_law_amender": ["*.prompt"],
    },
) 