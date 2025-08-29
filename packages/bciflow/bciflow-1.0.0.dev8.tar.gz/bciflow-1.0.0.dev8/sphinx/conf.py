# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_rtd_theme
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'bciflow'
copyright = '2025, Gabriel Henrique de Souza'
author = 'Gabriel Henrique de Souza'
release = '1.0.0.dev7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
        'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # Para suporte a Google-style ou NumPy-style docstrings
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# Defina o arquivo mestre (index.rst)
master_doc = 'index'

html_sidebars = {
    '**': [
        'sidebar.html',  # Template personalizado com links e barra de pesquisa
        'globaltoc.html',  # Índice global
        'relations.html',  # Links de navegação (anterior/próximo)
        'sourcelink.html',  # Link para o código-fonte
    ],
}

html_logo = '_static/logo_2.jpg'
html_theme_options = {
    'logo_only': True,  # Mostrar apenas a logo, sem o nome do projeto
    'style_nav_header_background': '#2980B9',  # Cor de fundo do cabeçalho
}