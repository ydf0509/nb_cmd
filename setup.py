# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='nb-cmd',
    version='0.1.0',
    description='万能接口生成器——你写一个 Python class，自动获得 CLI + REST API + Web UI 三种接口',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='ydf',
    author_email='ydf0509@sohu.com',
    url='https://github.com/ydf0509/nb_cmd',
    license='MIT',
    packages=find_packages(),
    package_data={'nb_cmd': ['ui/static/**/*']},
    python_requires='>=3.7',
    install_requires=[
        'typing_extensions>=3.7.4;python_version<"3.9"',
    ],
    extras_require={
        'api': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'pydantic>=1.8.0'],
        'web': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'websockets>=10.0'],
        'all': ['fastapi>=0.68.0', 'uvicorn>=0.15.0', 'pydantic>=1.8.0', 'websockets>=10.0'],
        'nb': ['nb_log'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
