from setuptools import setup, find_packages  # type: ignore

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ilt-py-lib",
    version="1.0.0",
    description="A python library for inverse Laplace transform of one dimensional and multidimensional data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9, <3.14",
    author="Davis Thomas Daniel, Josef Granwehr",
    author_email="davisthomasdaniel@gmail.com, j.granwehr@fz-juelich.de",
    license="LGPL-3.0-or-later",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    keywords=[
        "EPR", "NMR", "DRT", "Inverse Laplace transform",
        "Laplace inversion", "Relaxation", "Impedance"
    ],
    url="https://apps.fz-juelich.de/iltpy",
    project_urls={
        "Homepage": "https://apps.fz-juelich.de/iltpy",
        "Documentation": "https://apps.fz-juelich.de/iltpy",
        "Repository": "https://jugit.fz-juelich.de/iet-1/iltpy",
        "Issues": "https://jugit.fz-juelich.de/iet-1/iltpy/-/issues",
        "Changelog": "https://jugit.fz-juelich.de/iet-1/iltpy/-/blob/main/CHANGELOG"
    },
    packages=find_packages(),
    install_requires=[
        'scipy>=1.13.1,<=1.16.0',
        'numpy>1.25.1,<=2.3.1',
        'joblib>=1.4.2,<=1.5.1',
        'tqdm',
    ],
    extras_require={
        "develop": [
            "matplotlib",
            "pytest",
            "pytest-cov",
            "sphinx",
            "nbsphinx==0.9.5",
            "sphinx_rtd_theme==3.0.1",
            "sphinx-togglebutton==0.3.2",
            "sphinx_design==0.6.1",
            "sphinx-copybutton==0.5.2"
        ]
    },
    license_files=["LICENSE", "COPYING.LESSER.txt", "COPYING.txt","CITATION.cff"]
)
