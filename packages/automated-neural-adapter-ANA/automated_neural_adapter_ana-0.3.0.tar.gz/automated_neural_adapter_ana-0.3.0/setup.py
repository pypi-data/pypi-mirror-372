from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md file for PyPI
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="Automated_Neural_Adapter_ANA",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "datasets",
        "peft",
        "accelerate",
        "bitsandbytes",
    ],
    author="Rudransh Joshi",
    author_email="rudransh20septmber@gmail.com",
    description="A library for LoRA fine-tuning and model merging",
    long_description=long_description,  # <-- this is required
    long_description_content_type="text/markdown",
    url="https://drive.google.com/file/d/1jeBkmLz9x5qZMUdDthbeyDiIL4zFM4Y2/view?usp=drive_link",
    entry_points={
        "console_scripts": [
            "ana=ana.train:run",  # CLI command 'ana' runs the run() function in ana/train.py
        ],
    },
)
