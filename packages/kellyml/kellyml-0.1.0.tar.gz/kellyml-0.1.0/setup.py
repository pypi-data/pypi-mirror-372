from setuptools import setup, find_packages

setup(
    name="kellyml",  
    version="0.1.0",
    description="A lightweight ML helper package for preprocessing, evaluation, and models",
    author="Kelly",
    author_email="kellykoty@gmail.com",
    url="https://github.com/kellykoty/kellyml",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "numpy",
        "pandas",
        "imbalanced-learn"
    ],
    python_requires=">=3.7",
)