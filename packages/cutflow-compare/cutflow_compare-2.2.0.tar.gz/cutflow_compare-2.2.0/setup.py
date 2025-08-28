from setuptools import setup, find_packages

setup(
    name='cutflow_compare',
    version='2.2.0',  # Update this version as needed
    author='Ibrahim H.I. ABUSHAWISH',
    author_email='ibrahim.hamed2701@gmail.com',
    description='A Python package to compare cutflow histograms from ROOT files.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ibeuler/cutflow_compare',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas>=1.0',
        'uncertainties>=3.2.3',
        'prettytable>=3.0.0'
    ],
    entry_points={
        'console_scripts': [
            'cutflow_compare=cutflow_compare.cutflow_compare:main',
        ],
    },
    include_package_data=True,  # Ensures non-code files like README.md are included
    zip_safe=False,  # Ensures the package works when installed as a .egg
)