from setuptools import setup, find_packages

setup(
    name="Automated_Neural_Adapter_ANA",
    version="0.2.3",
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
    description="A library for LoRA fine-tuning and model merging",
    entry_points={
        "console_scripts": [
            "ana=ana.train:run",  # CLI command 'ana' runs the run() function in ana/main.py
        ],
    },
)
