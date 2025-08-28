from setuptools import setup, find_packages

setup(
    name="colortype",
    version="6.0.0a1",
    author="k_noob",
    description="ansi color and styling library for python console output",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/colortype",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
