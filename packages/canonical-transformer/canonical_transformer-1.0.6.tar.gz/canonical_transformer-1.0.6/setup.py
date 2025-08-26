from setuptools import setup, find_packages

setup(
    name='canonical_transformer',
    version='1.0.6',
    packages=find_packages(),
    install_requires=[
        req.strip() for req in open("requirements.txt", encoding="utf-8")
        if req.strip() and not req.strip().startswith("#")
    ],
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A Python module for preserving structural isomorphisms across data transformations, ensuring reversible and type-stable conversions between formats like DataFrame, JSON, and dict.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nailen1/canonical_transformer.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)