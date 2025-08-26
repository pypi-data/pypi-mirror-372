from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="pylaravel-orm",
    version="0.1.3",
    packages=find_packages(),
    author="Meysam Afghan",
    author_email="meysamnoori010@gmail.com",
    description="A Laravel-like ORM for MySQL in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hshmatullahnoor/pyLaravel-orm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "mysql-connector-python",
    ],
)
