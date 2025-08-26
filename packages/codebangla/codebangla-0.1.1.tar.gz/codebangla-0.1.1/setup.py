from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codebangla",
    version="0.1.1",
    author="Gemini",
    author_email="gemini@google.com",
    description="A Python transpiler to write Python code using Bangla keywords.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gemini/codebangla", # Replace with your actual URL
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Localization",
    ],
    python_requires='>=3.7',
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'codebangla=codebangla.cli:main',
        ],
    },
)