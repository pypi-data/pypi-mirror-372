from setuptools import setup, find_packages

setup(
    name='phdu',
    version='3.0.4',
    author="Jorge Medina Hernández",
    author_email='medinahdezjorge@gmail.com',
    packages=find_packages("."),
    url='https://github.com/medinajorge/PhD-utils',
    download_url='https://github.com/medinajorge/PhD-utils/archive/refs/tags/v2.6.7.tar.gz',
    description="Automatically store/load data in a tidy, efficient way. Includes functions for data visualization and analysis.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['science', 'statistics', 'tidy', 'project organization', 'project', 'organization', 'path', 'storage'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Office/Business",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3",
    install_requires=[
        'tidypath',
        'numba',
        'numpy',
        'pandas',
        'scipy',
        'colour',
        'Pillow',
    ],
    extras_require={
        "all": ["matplotlib", "plotly", "kaleido", "statsmodels", "rpy2", "colorlover", "sklearn"],
        "basic": ["matplotlib", "plotly", "kaleido", "colorlover", "sklearn"],
        "matplotlib": "matplotlib",
        "plotly": ["plotly", "kaleido"],
        "colorlover": "colorlover",
        'statsmodels': 'statsmodels',
        "r": "rpy2",
        "sklearn": "sklearn"
    },
)
