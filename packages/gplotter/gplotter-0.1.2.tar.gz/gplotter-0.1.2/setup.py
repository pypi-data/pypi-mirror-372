
from setuptools import setup, find_packages

setup(
    name='gplotter',
    version='0.1.2',
    author='Kishan Tamboli',
    author_email='kishant@iitbhilai.ac.in',
    description='CLI-based GNUPlot script generator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KishantLab/gplotter.git',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gplotter=gnuplot_gen.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)

