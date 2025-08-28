from setuptools import setup, find_packages

# Read README with UTF-8 encoding to avoid UnicodeDecodeError on Windows
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scrapery",  # Package name
    version="0.1.0",  # Current version
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="Fast, function-based HTML extraction library with CSS, XPath, chaining, and robust fetching.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scrapery",  # Replace with your repo
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/scrapery/issues",
        "Documentation": "https://github.com/yourusername/scrapery#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    packages=find_packages(where=".", include=["scrapery", "scrapery.*"]),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.27.0",
        "parsel>=1.9.1",
        "lxml>=5.2.0",
        "charset-normalizer>=3.3.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
