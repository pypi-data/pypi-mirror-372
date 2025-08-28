from setuptools import setup, find_packages

setup(
    name='argus-crawler',
    version='1.0.0',
    author='Arifi Razzaq',
    author_email='arifi.razzaq@example.com',
    description='A stealthy web crawler for intelligence gathering and cognitive noise analysis.',
    long_description='A project developed to analyze cognitive noise on various platforms, part of the legacy of Arifi Razzaq.',
    long_description_content_type='text/plain',
    url='https://github.com/razzaqinspires/ORACLE',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)