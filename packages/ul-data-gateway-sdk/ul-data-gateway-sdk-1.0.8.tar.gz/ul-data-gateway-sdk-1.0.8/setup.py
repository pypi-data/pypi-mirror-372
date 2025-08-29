from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul-data-gateway-sdk',
    version='1.0.8',
    description='Data gateway sdk',
    author='Unic-lab',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['data_gateway_sdk*']),
    include_package_data=True,
    package_data={
        '': ['*.yml', 'py.typed', 'crypto_algorithms/constants/kuz_tables.bin'],
        'data_gateway_sdk': ['py.typed'],
    },
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    platforms='any',
    install_requires=[
        'ul-unipipeline>=2.0.0',
        'asyncio-dgram==1.2.0',
        'asyncio==3.4.3',
        'timezonefinder==6.1.1',
        'pytest-env==0.8.1',
        'aiormq==6.7.7',
        'tenacity==8.2.3',
        # 'ul-data-aggregator-sdk==10.1.0',
        # 'ul-api-utils==9.1.0',
        # 'ul-pysmp==1.0.3',
        # 'ul-pyncp==1.0.5',
        # 'ul-data-logger-api-sdk==2.0.1',
        # 'ul-py-tool==2.1.4',
        # 'ul-db-utils==5.1.0',
        # 'ul-data-logger-sdk==3.0.4',
    ],
)
