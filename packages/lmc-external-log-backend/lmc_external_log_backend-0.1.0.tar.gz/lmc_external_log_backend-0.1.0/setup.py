from setuptools import setup, find_packages

setup(
    name='lmc_external_log_backend',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'torch',
        'lmcache',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='External logging backend implementation for LMCache',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/lmc_external_log_backend',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)