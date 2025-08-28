from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='st_oxview',
    version='0.1.6',
    author='Luca Monari',
    author_email='Luca.Monari@mr.mpg.de',
    url="https://github.com/Lucandia/st_oxview",
    description='A Streamlit component for coarse-grained DNA/RNA visualization with OxView',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "streamlit",
        "matplotlib",
        "IPython",
    ],
)