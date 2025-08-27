from setuptools import setup, find_packages

setup(
    name='filewave',
    version='0.0.1',
    author='66Studio',
    author_email='',
    description='A module for convenient file management',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)