
from setuptools import setup, find_packages
import os

# Read the README.md for the long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CVNN_Jamie',
    version='0.1.7',
    description='A neural network framework supporting complex-valued neural networks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jamie Keegan-Treloar',
    author_email='jamie.kt@icloud.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.7',
)
