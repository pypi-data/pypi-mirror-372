# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stdexcept",
    version="0.1.0",
    author="RSC-E Studio",
    author_email="rscestudio114514@gmail.com",
    description="Terminal Raise Error Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://pymodule.rsc-studio.com/stdexcept",
    #package_dir={"": "stdexcept"},
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    keywords=["output", "stdout", "stderr", "suppress", "mute", "silence"],
    python_requires=">=3.7",
)