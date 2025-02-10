#!/usr/bin/env python3

from setuptools import setup, find_packages

def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name='shortcap',
    version='1.0.5',
    packages=find_packages(),
    install_requires=get_requirements(),
    extras_require = {
        'local_whisper': ["openai-whisper"],
    },
    package_data={
        'shortcap': [
            'assets/*',
            'assets/fonts/*',
            'assets/fonts/*.ttf',
        ],
    },
    include_package_data=True,
    url='https://github.com/SmartClipAI/shortcap',
    license='MIT',
    author='SmartClipAI',
    author_email='jacky.xbb@gmail.com',
    description='Add Automatic Captions to Short Videos with AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'shortcap=shortcap.cli:main',
        ],
    },
)