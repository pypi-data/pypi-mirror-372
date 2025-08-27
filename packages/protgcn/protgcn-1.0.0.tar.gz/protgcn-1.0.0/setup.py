from setuptools import setup
from codecs import open
from os import path
from setuptools_scm import get_version

dir_path = path.abspath(path.dirname(__file__))

with open(path.join(dir_path, 'PYPI_Description.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='protgcn',
    license='MIT',
    url='https://github.com/your-username/ProtGCN',
    description='State-of-the-art protein sequence design using Graph Convolutional Networks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['protgcn', 'protein design', 'graph neural networks', 'bioinformatics'],

    author='Mahatir Ahmed Tusher, Anik Saha, Md. Shakil Ahmed',
    author_email='protgcn@example.com',

    use_scm_version={'local_scheme': 'no-local-version'},

    setup_requires=['setuptools_scm'],
    install_requires=[
        'torch>=1.9.0',
        'numpy>=1.19.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0',
        'tqdm>=4.60.0',
        'flask>=2.0.0',
        'werkzeug>=2.0.0'
    ],

    include_package_data=True,
    
    # Include all Python modules from scripts and root
    py_modules=['app', 'visualization', 'quick_validation'],
    
    # Include packages directory
    packages=['gcndesign', 'scripts'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10', 
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    
    python_requires='>=3.8',
    
    # Add package data - include templates and parameter files
    package_data={
        'gcndesign': ['params/*.pkl'],
        '': ['templates/*.html'],
    },
    
    # Add entry points for command-line tools
    entry_points={
        'console_scripts': [
            'protgcn-predict=scripts.protgcn_predict:main',
            'protgcn-app=app:main',
            'protgcn-validate=quick_validation:main',
        ],
    },
)