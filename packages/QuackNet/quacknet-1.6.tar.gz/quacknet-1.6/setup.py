from setuptools import setup, find_packages

setup(
    name='QuackNet',
    version='1.6',
    description='A lightweight educational deep learning library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SirQuackPng/QuackNet',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pillow',
        'matplotlib',
    ],
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
) 