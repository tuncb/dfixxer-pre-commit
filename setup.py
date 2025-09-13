from setuptools import setup

setup(
    name="dfixxer-pre-commit",
    version="0.1.0",
    description="Pre-commit hook for dfixxer (Delphi/Pascal code formatter)",
    author="Tunc Bahcecioglu",
    author_email="tuncbah@example.com",
    url="https://github.com/tuncb/dfixxer-pre-commit",
    py_modules=["dfixxer_hook"],
    entry_points={
        "console_scripts": [
            "dfixxer-hook=dfixxer_hook:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
    ],
)