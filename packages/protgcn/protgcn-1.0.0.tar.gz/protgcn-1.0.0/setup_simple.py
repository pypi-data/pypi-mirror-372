from setuptools import setup, find_packages
from codecs import open
from os import path

dir_path = path.abspath(path.dirname(__file__))

with open(path.join(dir_path, 'PYPI_Description.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='protgcn',
    version='1.0.0',  # Fixed version for testing
    license='MIT',
    url='https://github.com/your-username/ProtGCN',
    description='State-of-the-art protein sequence design using Graph Convolutional Networks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['protgcn', 'protein design', 'graph neural networks', 'bioinformatics'],

    author='Mahatir Ahmed Tusher, Anik Saha, Md. Shakil Ahmed',
    author_email='protgcn@example.com',

    packages=find_packages(include=['gcndesign', 'gcndesign.*', 'scripts', 'scripts.*']),
    py_modules=['app', 'visualization', 'quick_validation'],
    
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

    python_requires='>=3.8',
    
    include_package_data=True,
    
    package_data={
        'gcndesign': ['params/*.pkl'],
        '': ['templates/*.html'],
    },
    
    entry_points={
        'console_scripts': [
            'protgcn-predict=scripts.protgcn_predict:main',
            'protgcn-app=app:main',
            'protgcn-validate=quick_validation:main',
        ],
    },
    
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
)
