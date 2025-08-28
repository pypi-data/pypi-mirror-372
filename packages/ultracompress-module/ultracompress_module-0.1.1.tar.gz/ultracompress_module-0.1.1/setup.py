from setuptools import setup, find_packages

setup(
    name="ultracompress_module",
    version="0.1.1",
    description="Ultra JSON compressor/decompressor",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Béret",
    author_email="admin@levraiberet.ovh",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
    "msgpack",
    "zstandard",
    "tqdm",
    "ijson",
    "base91",
    "brotli",
    ]
)