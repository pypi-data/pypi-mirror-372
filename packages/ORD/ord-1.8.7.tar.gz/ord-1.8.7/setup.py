from setuptools import setup, find_packages
from io import open


def read(filename):
    """Прочитаем наш README.md для того, чтобы установить большое описание."""
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


setup(
    name='ORD',
    version='1.8.7',
    author='Vladimir Smirnov',
    author_email='volodya@brandshop.ru',
    description='Module for working with the ATOL cash register driver',
    url='https://brandshop.ru',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
)
