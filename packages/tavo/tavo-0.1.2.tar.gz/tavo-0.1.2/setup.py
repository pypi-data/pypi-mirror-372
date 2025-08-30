from setuptools import setup, find_packages
import io
import os

# Read README.md for long description
def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()

setup(
    name="tavo",
    version="0.1.2",
    author="Hallel",
    author_email="admin@cyberwizdev.com.ng",
    description="Tavo full-stack framework CLI - Python backend + Rust/SWC React SSR",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/cyberwizdev/tavo",
    license="MIT",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Rust",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(
        include=["tavo_cli", "tavo_core", "tavo_cli.*", "tavo_core.*"]
    ),
    include_package_data=True,
    package_data={
        "tavo_core": [
            "*.rs",
            "*.toml",
            "frontend/**",
            "templates/**",
            "static/**",
        ],
    },
    exclude_package_data={
        "": ["*.pyc", "__pycache__", "*.pyo"],
    },
    install_requires=[
        "anyio>=4.0.0",
        "certifi>=2025.0.0",
        "charset-normalizer>=3.0.0",
        "click>=8.0.0",
        "colorama>=0.4.0",
        "idna>=3.0.0",
        "markdown-it-py>=3.0.0",
        "mdurl>=0.1.0",
        "Pygments>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.0.0",
        "rich>=13.0.0",
        "shellingham>=1.0.0",
        "sniffio>=1.0.0",
        "starlette>=0.47.0",
        "typer>=0.15.0",
        "typing_extensions>=4.0.0",
        "urllib3>=2.0.0",
        "watchfiles>=1.0.0",
        "websockets>=14.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tavo=tavo_cli.main:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/cyberwizdev/tavo",
        "Bug Tracker": "https://github.com/cyberwizdev/tavo/issues",
    },
)
