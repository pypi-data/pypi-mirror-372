
from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
readme_path = this_dir / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="principal_package",             
    version="0.2.0",
    description="Librería proyecto brasil",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian Castro",        
    license="MIT",                    
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "full": [
            "scikit-learn>=1.4",
            "umap-learn>=0.5.5",
            "hdbscan>=0.8.38",
            "jinja2>=3.1",
            "openpyxl>=3.1",
            "tqdm>=4.65",
            "joblib>=1.3",
            "matplotlib>=3.8",
            "numpy>=1.23",
            "pandas>=1.5",
            "seaborn>=0.12",
            "plotly>=5.15",
        ]
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Intended Audience :: Science/Research",
    ],
)