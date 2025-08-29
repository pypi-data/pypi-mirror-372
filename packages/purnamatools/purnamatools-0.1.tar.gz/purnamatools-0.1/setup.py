from setuptools import setup, find_packages
from pathlib import Path

# ambil long_description dari README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="purnamatools",
    version="0.1",
    author="Nama Kamu",
    author_email="email@kamu.com",
    description="Paket Python untuk mempermudah tahap awal pembuatan model sebelum analisis lebih lanjut",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "numpy",
        "seaborn",
        "matplotlib",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="data-science machine-learning feature-selection model-analysis",
)
