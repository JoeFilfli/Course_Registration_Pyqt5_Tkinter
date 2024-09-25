# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
<<<<<<< HEAD
sys.path.insert(0, os.path.abspath(r'C:\Users\Administrator\OneDrive - American University of Beirut\AUB\Fall24-25\EECE 435L\Ps-Me\Lab2'))



project = 'EECE435_LAB'
copyright = '2024, Joe Filfli'
author = 'Joe Filfli'
=======
sys.path.insert(0, os.path.abspath(r"C:\Users\manso\OneDrive\Desktop\Fall 2024\EECE 435L\Lab 2 NEW"))


project = 'EECE435L'
copyright = '2024, Mansour Allam'
author = 'Mansour Allam'
>>>>>>> 653fbf1a584a6af3f4f2c5773c296f876dd9686e
release = '0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
'sphinx.ext.autodoc',
'sphinx.ext.viewcode',
'sphinx.ext.napoleon' ]

<<<<<<< HEAD
=======

>>>>>>> 653fbf1a584a6af3f4f2c5773c296f876dd9686e
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


<<<<<<< HEAD
=======

>>>>>>> 653fbf1a584a6af3f4f2c5773c296f876dd9686e
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
