from setuptools import setup
from bigquantdai import __version__

# 读取 README.md 内容作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bigquantdai",
    version=__version__,
    author="BigQuant",
    author_email="bigquant@bigquant.com",
    description="bigquant 数据SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bigquant.com",
    project_urls={"Documentation": "https://bigquant.com/wiki/doc/sdk-gMEOV2bGYi"},
    packages=["bigquantdai"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy<2.0",
        "pandas>=1.2.2",
        "pyarrow==14.0.2"
    ],
    keywords="数据SDK, dai, bigquant",
    license="MIT",
    # build_with_nuitka=True,

)
