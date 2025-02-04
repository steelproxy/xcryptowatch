from setuptools import setup, find_packages

setup(
    name="xcryptowatch",
    version="0.1.0",
    author="Collin Rodes",
    author_email="steelproxy@protonmail.com",
    description="A program to monitor crypto trends on social media.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/steelproxy/xcryptowatch",
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here, e.g.
        "postalsend",
        "jsonschema",
        "tweepy",
        "openai"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "xcryptowatch=xcryptowatch.xcryptowatch:main",
        ],
    },
)
