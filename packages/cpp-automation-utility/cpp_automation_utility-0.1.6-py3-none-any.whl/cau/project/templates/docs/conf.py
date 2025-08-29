import datetime
import pathlib
import subprocess as sp

config_directory = pathlib.Path(__file__).parents[0]
pages_directory = pathlib.Path(__file__).parents[2]/"pages"
generated_doxygen = config_directory/"doxygen"/"xml"

project = '{{ meta_data.name }}'
author = ''
copyright = f'{datetime.datetime.now().year}, {author}'

extensions = ["breathe", "myst_parser", "sphinx_design", "sphinx_exercise", "sphinxcontrib.bibtex"]

templates_path = ['_templates']
exclude_patterns = []

highlight_language = 'c++'

html_theme = 'sphinx_book_theme'
html_title = project
# html_logo = str(pages_directory / "assets" / "{{ meta_data.name }}.svg")
# html_favicon = html_logo
html_theme_options = {"home_page_in_toc": True}
html_static_path = ['_static']

myst_enable_extensions = ["dollarmath", "amsmath"]
myst_fence_as_directive = ["mermaid"]
myst_heading_anchors = 3

numfig = True

breathe_projects = {project: str(generated_doxygen)}
breathe_default_project = project
breathe_default_members = ('members', 'undoc-members')

bibtex_bibfiles = [
    str(config_directory/"refs.bib"),
]

sp.call("doxygen Doxyfile.in", shell=True)
sp.call("breathe-apidoc doxygen/xml -o generated -f -m --generate class,interface,struct,union,file", shell=True)
