from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atikin-cache",
    version="1.0.0",
    author="Atikin Verse",
    author_email="atikinverse@gmail.com", 
    description="High-performance in-memory caching library with TTL, LRU eviction, and persistence.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atikinverse/atikin-cache",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="cache caching memory ttl lru performance atikin cache",
)
