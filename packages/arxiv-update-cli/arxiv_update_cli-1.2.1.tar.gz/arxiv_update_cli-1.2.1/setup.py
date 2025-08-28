#! /usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="arxiv_update_cli",
    version="1.2.1",
    description="Fetch new articles on arXiv by keywords",
    author="Juliette Monsel",
    author_email="j_4321@protonmail.com",
    license="MIT",
    url="https://gitlab.com/j_4321/arxivscript",
    py_modules=["arxiv_update_cli"],
    entry_points={
        'console_scripts': ['arxiv-update-cli = arxiv_update_cli:main']
    },
    long_description=long_description,
    long_description_content_type="text/x-rst",                       
    install_requires=['feedparser'],
    extras_require={
        'Store password in system keyring': ["keyring"],
        'Progressbar for file downloads': ["tqdm"],
        'Import articles in Zotero Library': ["pyzotero"],
        'Tab autocompletion in interactive mode': ["pyreadline3;sys_platform == 'win32'"],
    },
    classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Intended Audience :: Science/Research',
              'Environment :: Console',
              'Topic :: Scientific/Engineering',
              'Operating System :: OS Independent',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3',
              'Natural Language :: English',
      ],
)
