#!/usr/bin/env python3
"""
Annotex - Annotation Tool
Professional annotation tool for computer vision datasets
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI-Powered Annotation Tool for Computer Vision"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="annotex",
    version="2.0.8",
    author="Randika K. Makumbura",
    author_email="randikamk.96@gmail.com",
    description="AI-Powered Annotation Tool for Computer Vision Datasets",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/RandikaKM/annotex",
    project_urls={
        "Bug Reports": "https://github.com/RandikaKM/annotex/issues",
        "Source": "https://github.com/RandikaKM/annotex",
        # "Documentation": "https://github.com/RandikaKM/annotex/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # "License :: RKM License",
        # "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords="annotation, computer vision, AI, machine learning, YOLO, dataset, labeling",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "gpu": ["torch", "torchvision"],
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "annotex=annotex.main:main",
            "annotex-gui=annotex.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "annotex": ["assets/*", "assets/screenshots/*"],
    },
    zip_safe=False,
)