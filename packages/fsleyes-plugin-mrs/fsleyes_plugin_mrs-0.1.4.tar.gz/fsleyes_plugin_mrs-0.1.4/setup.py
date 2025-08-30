#!/usr/bin/env python

from setuptools import setup

version = {}
with open("version.py") as f:
    exec(f.read(), version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fsleyes-plugin-mrs',

    version=version["__version__"],

    description='FSLeyes extension for viewing MRS(I) data formatted as NIfTI-MRS.',
    author='William Clarke, University of Oxford',
    author_email='william.clarke@ndcn.ox.ac.uk',
    url='https://git.fmrib.ox.ac.uk/wclarke/fsleyes-plugin-mrs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent"],

    python_requires='>=3.10',

    packages=['fsleyes_plugin_mrs'],

    entry_points={

        'fsleyes_views': [
            'MRS view = fsleyes_plugin_mrs.views:MRSView',
        ],

        'fsleyes_controls': [
            'NIfTI-MRS = fsleyes_plugin_mrs.controls:MRSDimControl',
            'MRS control = fsleyes_plugin_mrs.controls:MRSControlPanel',
            'MRS toolbar = fsleyes_plugin_mrs.controls:MRSToolBar',
            'MRSI results = fsleyes_plugin_mrs.tools:MRSResultsControl',
        ],

        'fsleyes_tools': [
            'Load MRSI fit = fsleyes_plugin_mrs.tools:MRSFitTool',
        ],

        'fsleyes_layouts': [
            'mrs = fsleyes_plugin_mrs.layouts:mrs_fsleyes_layout'
        ]
    },

    package_data={'fsleyes_plugin_mrs': ['icons/*.png']},

    install_requires=['fsleyes>=1.0.10',
                      'file-tree>=1.6.1,<=2.0']
)
