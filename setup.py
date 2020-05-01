from setuptools import setup, find_packages

setup(
    name='mytools',
    version='1.0.1',
    description="This is my own packages used to do my data analysis",
    author='Yaopeng Ma',
    author_email="sdumyp@126.com",
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'matplotlib', 'pyedflib', 'biosppy']
)