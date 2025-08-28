from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="processflow",
    version="1.0.0",  # Fresh start with pure Python version
    author="CS Goh", 
    author_email="your.email@example.com",
    description="A Python package for creating process flow diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guochen2011gc/processflow",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.9",
    install_requires=[
        "rich>=10.0.0",
        "Pillow>=8.0.0",
        "drawsvg>=1.8.0",
    ],
    include_package_data=True,
    zip_safe=True,  # Pure Python, so zip-safe
)