from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as readme:
    README = readme.read()
try:
    with open("requirements.txt", encoding="utf-8") as req:
        REQUIREMENTS = [r.partition("#")[0] for r in req if not r.startswith("-e")]
except OSError:
    # Shouldn't happen
    REQUIREMENTS = []

print(REQUIREMENTS)
VERSION = "1.0.0"

setup(
    name="b4p",
    description="=this package is used to handle the energyMarket smart contract",
    long_description=README,
    author="Pietro Piccini",
    author_email="pietro.piccini@hotmail.com",
    url="https://github.com/BC4P/energyMarket.git",
    version=VERSION,
    packages=find_packages(where=".", exclude=["tests"]),
    package_dir={"b4p": "b4p"},
    package_data={},
    install_requires=REQUIREMENTS,
    zip_safe=False,
    include_package_data=True
)