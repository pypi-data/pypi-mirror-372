from setuptools import setup, find_packages

setup(
    name='binDB',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pycountry',
        'pycountry-convert',
    ],
    author='islamraisul796',
    author_email='islamraisul796@gmail.com', # Using a placeholder email based on username
    description='A Python library for retrieving BIN (Bank Identification Number) information.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
