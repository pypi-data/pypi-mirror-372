from setuptools import setup, find_packages

setup(
    name='CVNN_Jamie',
    version='0.1.1',
    description='A neural network framework supporting complex-valued neural networks',
    author='Jamie Keegan-Treloar',
    author_email='jamie.kt@icloud.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.7',
)
