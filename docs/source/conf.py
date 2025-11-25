import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath("../../src"))


def get_version():
    try:
        # Get the latest git tag (--always option allows commit hash as fallback)
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--always"], universal_newlines=True
        ).strip()
        return tag
    except subprocess.CalledProcessError:
        # Return default version if no git tag exists
        return "0.1.0"


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "crypto-api-client"
copyright = "2025, Takahito Urai"
author = "Takahito Urai"
release = get_version()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # For reading source code
    "sphinx.ext.napoleon",  # For parsing docstrings
    "sphinxcontrib.autodoc_pydantic",  # For generating Pydantic documentation
    "sphinxcontrib.mermaid",  # For embedding Mermaid diagrams
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

# -- Internationalization configuration ------------------------------------
# https://www.sphinx-doc.org/en/master/usage/advanced/intl.html
locale_dirs = ['locale/']
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Autodoc configuration ---------------------------------------------------
# Configuration to prevent duplicate object definitions
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
    'undoc-members': True,
}

# Avoid duplicates from __init__.py imports
autodoc_mock_imports = []

# Configuration for more detailed control
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Suppress warnings for duplicate objects
suppress_warnings = [
    'app.add_node',
    'app.add_directive',
    'app.add_role',
    'app.add_generic_role',
    'app.add_source_parser',
    'autosummary',
    'autodoc.import_object',
    'ref.python',  # Suppress cross-reference warnings for multiple targets
    'autodoc',     # Suppress autodoc-related warnings
    'docutils',    # Suppress docstring syntax errors
    'misc.highlighting_failure',  # Suppress JSON syntax highlighting errors
]

# Skip Module contents section in __init__.py for Sphinx autodoc
def skip_module_contents(app, what, name, obj, skip, options):
    """Filter to avoid duplicates in Module contents section of __init__.py"""
    # Skip objects defined in package __init__.py
    if what == "module" and name.endswith(".__init__"):
        return True

    # Skip classes/functions at package level that are already defined in individual modules
    module_parts = name.split('.')
    if len(module_parts) >= 3:
        package_path = '.'.join(module_parts[:-1])

        # Skip known duplicate patterns
        skip_patterns = [
            'crypto_api_client.bitflyer.models',
            'crypto_api_client.bitbank.models',
            'crypto_api_client.bitflyer.requests',
            'crypto_api_client.bitbank.requests'
        ]

        if any(package_path == pattern for pattern in skip_patterns):
            return True

    return skip

def setup(app):
    """Sphinx configuration setup"""
    app.connect('autodoc-skip-member', skip_module_contents)

    # Raise warning level (show only ERRORs)
    import logging
    logging.getLogger('sphinx').setLevel(logging.ERROR)
    logging.getLogger('autodoc').setLevel(logging.ERROR)
    logging.getLogger('docutils').setLevel(logging.ERROR)

# Pydantic configuration (prevent JSON schema errors)
autodoc_pydantic_model_show_json_schema = False
autodoc_pydantic_settings_show_json_schema = False
autodoc_pydantic_field_show_constraints = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_field_summary = False
