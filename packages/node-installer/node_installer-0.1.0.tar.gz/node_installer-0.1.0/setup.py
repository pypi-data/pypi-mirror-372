#setup.py
from setuptools import setup

setup(
    name="node-installer",
    version="0.1.0",
    description="Install Node.js silently via CMD on Windows",
    author="Antony",
    py_modules=["installer"],
    entry_points={
        "console_scripts": [
            "install-node=installer:install_node"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",
)
