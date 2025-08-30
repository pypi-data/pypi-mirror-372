project = 'Promium'
copyright = '2020, evo.company'
author = 'Denis Korytkin, Nataliia Guieva, Roman Zaporozhets, Vladimir Kritov, Oleh Dykusha'

extensions = [
    'sphinx.ext.intersphinx',
    'sphinxemoji.sphinxemoji',
    'sphinx_autobuild',
    # 'myst_parser',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.7', None),
}
templates_path = ['_templates']
source_suffix = ['.rst', '.md']
master_doc = 'index'
source_parsers = {
   '.md': 'recommonmark.parser.CommonMarkParser',
}

# html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'display_version': False,
}
html_context = {
    'display_gitlab': True,
    'gitlab_host': 'gitlab.evo.dev',
    'gitlab_user': 'qa-automation',
    'gitlab_    repo': 'qa-automation.git-doc.evo.dev/promium',
    'gitlab_version': 'master',
    'conf_py_path': '/source/',
}


html_static_path = ['_static']

html_css_files = [
        'custom.css',
]

html_favicon = 'favicon.ico'
