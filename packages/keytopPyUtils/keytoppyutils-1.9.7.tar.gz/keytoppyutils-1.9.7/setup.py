# kt-py-redis\setup.py
from setuptools import setup, find_packages

setup(
    name='keytopPyUtils',
    version='1.9.7',
    packages=find_packages(),
    install_requires=[
        'markdown',
        'bs4',
        'python-docx',
        'weasyprint==52.5',
        'esdk-obs-python',
        'matplotlib'
    ],
    author='zhangjukai',
    author_email='zhangjukai@keytop.com.cn',
    description='keytop python utils',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)