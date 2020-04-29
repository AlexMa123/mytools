from setuptools import setup, find_namespace_packages

setup(
    name='mytools',
    version='1.0.0',
    description="This is my own packages used to do my data analysis",
    author='Yaopeng Ma',
    author_email="sdumyp@126.com",
    packages=find_namespace_packages(include=["mytools.*"]),
    install_requires=['numpy', 'scipy', 'matplotlib', 'pyedflib']
)
