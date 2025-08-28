from setuptools import setup, find_packages
from pathlib import Path

def parse_requirements(filename):
    with open(Path(__file__).parent / filename, encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="s3-lifecycle-delta",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    author="Fernando Oliveira Pereira",
    author_email="oliveira-fernando1@hotmail.com",
    description="A small Python library to compute and apply deltas on AWS S3 lifecycle",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-library",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=parse_requirements("requirements.txt"),
)
