"""
Setup configuration for MathDiagram library
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mathdiagram",
    version="1.0.0",
    author="MathDiagram Library",
    author_email="contact@mathdiagram.com",
    description="Generic mathematical diagram generation library for any topic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathdiagram/mathdiagram",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    install_requires=[
        "matplotlib>=3.3.0",
        "numpy>=1.18.0",
        "scipy>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "mathdiagram=mathdiagram.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mathdiagram": ["templates/*.json", "data/*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/mathdiagram/mathdiagram/issues",
        "Source": "https://github.com/mathdiagram/mathdiagram",
        "Documentation": "https://mathdiagram.readthedocs.io/",
    },
)
