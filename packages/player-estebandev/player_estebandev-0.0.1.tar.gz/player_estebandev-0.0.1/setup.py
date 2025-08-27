import setuptools
from pathlib import Path


descripcion = Path('./README.md').read_text()

setuptools.setup(
    name="player-estebandev",
    version="0.0.1",
    long_description=descripcion,
    packages=setuptools.find_packages(
        exclude=["mocks","tests"]
    )
)

