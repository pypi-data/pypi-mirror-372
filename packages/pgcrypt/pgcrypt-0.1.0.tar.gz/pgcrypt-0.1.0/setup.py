import shutil
from setuptools import (
    find_packages,
    setup,
)


shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("pgcrypt.egg-info", ignore_errors=True)

with open(file="README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pgcrypt",
    version="0.1.0",
    packages=find_packages(),
    author="0xMihalich",
    author_email="bayanmobile87@gmail.com",
    description=(
        "PGCopy dump packed into LZ4, ZSTD or "
        "uncompressed with meta data information packed into zlib."
    ),
    url="https://github.com/0xMihalich/pgcrypt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
)
