import os
import sys

# Agrega el directorio raíz del proyecto
sys.path.insert(0, os.path.abspath('../../..'))

project = 'Biblioteca Popular Nelly Llorens'
author = 'IGNACIO ALCANIZ'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'es'

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']




