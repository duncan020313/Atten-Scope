## setup.py
from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup

install_requires = [
    "numpy",
    "torch",
]

setup(
    name="AttenScope",
    version="0.1",
    author="Dongjae Lee",
    author_email="dongjae.lee@prosys.kaist.ac.kr",
    install_requires=install_requires,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
)
