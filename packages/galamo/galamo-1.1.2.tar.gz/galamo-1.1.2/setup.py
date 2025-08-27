from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="galamo",
    version="1.1.2",
    author="Jashanpreet Singh Dingra",
    author_email="astrodingra@gmail.com",
    description=(
        "An open source Python package for comprehensive galaxy analysis, "
        "integrating machine learning and statistical methods. It provides "
        "automated tools for morphology classification, kinematics, photometry, "
        "and spectral analysis to aid astrophysical research."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.galamo.org",
    project_urls={
        "Source Code": "https://github.com/galamo-org/galamo",
        "Documentation": "https://galamo.org/docs",
        "Bug Tracker": "https://github.com/galamo-org/galamo/issues",
        "Model Repository": "https://huggingface.co/astrodingra/galamo",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "tensorflow>=2.10.0",
        "numpy>=1.23.0",
        "pandas>=1.5.0",
        "scipy>=1.9.0",
        "opencv-python>=4.6.0",
        "joblib>=1.2.0",
        "matplotlib>=3.6.0",
        "termcolor>=2.0.0",
        "requests>=2.28.0",
        "huggingface_hub>=0.14.0",
        "tqdm>=4.64.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.10",
)
