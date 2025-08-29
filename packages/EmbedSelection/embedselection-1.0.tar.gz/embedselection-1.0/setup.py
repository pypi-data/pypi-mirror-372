from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='EmbedSelection',
    version='1.0',
    author='Ilias, Hongliu',
    author_email='ilias.driouich@amadeus.com;hongliu.cao@amadeus.com',
    description='Embedding selection: A tool for selecting the best embedding model for your use case',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AmadeusITGroup/EmbSelection',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas>=1.1.0',
        'numpy>=1.19.0',
    ],
    tests_require=[
        'pytest>=6.0.0',
    ],
    entry_points={
        'console_scripts': [
            'EmbedSelection=run.run:main',
    ],
    },
    python_requires='>=3.6',
)
