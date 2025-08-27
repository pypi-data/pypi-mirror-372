from setuptools import setup, find_packages

setup(
    name="volcanic_checker",
    version="0.1.1",
    description="Fetch and handle volcanic activity alerts from JMA",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mellllonsoda/volcanic_checker",
    author="mellllonsoda",
    author_email="ymellllonsoda0419@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,  # package_data を使う場合
    package_data={
        "volcanic_checker": ["volcanolist.json"]
    },
    install_requires=[
        "requests>=2.0",
        "beautifulsoup4>=4.0"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "volcanic-checker=volcanic_checker.main:main",
        ],
    },
)
