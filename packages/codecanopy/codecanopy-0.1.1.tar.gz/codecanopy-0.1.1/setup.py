from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codecanopy",
    version="0.1.1",
    author="Sawradip Saha",
    author_email="sawradip0@gmail.com",
    description="Give LLMs perfect context about your codebase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sawradip/CodeCanopy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "pathspec>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "codecanopy=codecanopy.cli:main",
        ],
    },
)
