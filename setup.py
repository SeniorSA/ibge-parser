import setuptools

with open(file="README.md", mode="r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ibge-parser",
    version="1.0.2",
    author="Senior Sistemas - Senior Labs",
    author_email="research@senior.com.br",
    description="IBGE Parser is a Python library to get microdata from IBGE - (Instituto Brasileiro de Geografia e Estatística) census and convert the data to readable CSV files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SeniorSA/ibge-parser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
      'logzero==1.5.0'
    ],
    python_requires='>=3.6',
)