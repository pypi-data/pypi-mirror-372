from setuptools import setup, find_packages

# Read README with UTF-8 encoding to avoid UnicodeDecodeError on Windows
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="datadigger",  # Name of your package
    version="0.1.8",  # Current version
    install_requires=[
        # Example dependencies (uncomment if needed)
        # "pandas==2.0.2",
        # "beautifulsoup4==4.12.2",
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description=(
        "The package is geared towards automating text-related tasks and is "
        "useful for data extraction, web scraping, and text file management."
    ),
    long_description=long_description,  # README content
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatically discover all packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
