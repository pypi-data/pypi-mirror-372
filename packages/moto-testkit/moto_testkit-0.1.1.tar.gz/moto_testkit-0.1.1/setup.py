from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="moto-testkit",
    version="1.0.0",
    packages=find_packages(),
    description="Uma biblioteca para demonstrar como subir no pypi",
    author="Rafael da Silva",
    author_email="rafadasilva98@gmail.com",
    url="https://github.com/RafaeldaSilvaa/moto-testkit",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
)