from setuptools import setup

setup(
    name = 'python-requestr',
    packages = ['requestr',],
    install_requires=['python-objectifier', 'beautifulsoup4'],
    version = '0.12',
    description = 'requestr',
    url = 'https://github.com/xjxckk/python-requestr/',
    download_url = 'https://github.com/xjxckk/python-requestr/archive/refs/tags/v0.1.tar.gz',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
    )