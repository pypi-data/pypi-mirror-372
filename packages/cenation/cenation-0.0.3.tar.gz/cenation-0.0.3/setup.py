from setuptools import setup, find_packages

setup(
    name="cenation",
    version="0.0.3",
    author="john cena",
    author_email="cena@17.com",
    description="A small example package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Homepage": "https://github.com/pypa/sampleproject",
        "Issues": "https://github.com/pypa/sampleproject/issues",
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
)

