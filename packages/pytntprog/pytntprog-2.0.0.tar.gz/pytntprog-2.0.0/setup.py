from setuptools import setup


setup(
    name="pytntprog",
    version="2.0.0",
    description="pytntprog displays the program of tnt tv in France",
    long_description="The complete description/installation/use/FAQ is available at : https://github.com/thib1984/pytntprog#readme",
    url="https://github.com/thib1984/pytntprog",
    author="thib1984",
    author_email="thibault.garcon@gmail.com",
    license="MIT",
    license_files=[],
    packages=["pytntprog"],
    install_requires=["colorama","termcolor","columnar","requests"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "pytntprog=pytntprog.__init__:pytntprog"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
