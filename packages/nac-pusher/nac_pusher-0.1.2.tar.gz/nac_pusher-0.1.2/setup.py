from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nac-pusher",
    version="0.1.2",
    author="Necoarc",
    author_email="3306601284@qq.com",
    description="A Python package for pushing messages to Feishu (Lark)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nac-pusher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "lark-oapi>=1.4.22",
    ],
)