from setuptools import setup, find_packages

setup(
    name="vohid-telegram-bot",
    version="0.1.0",
    author="Vohid_23",
    description="A simple python telegram library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VOHID2308/py-gram-bot.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
