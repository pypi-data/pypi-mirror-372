# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime

from docutils import nodes  # type: ignore[import-untyped]
from sphinx.addnodes import pending_xref  # type: ignore[import-not-found]
from sphinx.application import Sphinx  # type: ignore[import-not-found]
from sphinx.environment import BuildEnvironment  # type: ignore[import-not-found]

project = "Uncountable SDK"
copyright = f"{datetime.datetime.now(tz=datetime.UTC).date().year}, Uncountable Inc"
author = "Uncountable Inc"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_favicon",
]
myst_enable_extensions = ["fieldlist", "deflist", "colon_fence"]

autoapi_dirs = ["../uncountable"]
autoapi_options = [
    "members",
    "inherited-members",
    "undoc-members",
]
autoapi_root = "api"
autoapi_ignore = ["*integration*"]
autodoc_typehints = "description"
autoapi_member_order = "groupwise"
autoapi_own_page_level = "class"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

python_use_unqualified_type_names = True
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = "Python SDK"
html_static_path = ["static"]
html_logo = "static/logo_blue.png"

favicons = [
    "favicons/android-chrome-192x192.png",
    "favicons/android-chrome-512x512.png",
    "favicons/apple-touch-icon.png",
    "favicons/favicon-16x16.png",
    "favicons/favicon-32x32.png",
    "favicons/mstile-150x150.png",
    "favicons/safari-pinned-tab.svg",
]


def _hook_missing_reference(
    _app: Sphinx, _env: BuildEnvironment, node: pending_xref, contnode: nodes.Text
) -> nodes.reference | None:
    """
    Manually resolve reference when autoapi reference resolution fails.
    This is necessary because autoapi does not fully support type aliases.
    """
    # example reftarget value: uncountable.types.identifier_t.IdentifierKey
    target = node.get("reftarget", "")

    # example refdoc value: api/uncountable/types/generic_upload_t/GenericUploadStrategy
    current_doc = node.get("refdoc", "")

    if not target.startswith("uncountable"):
        return None

    target_module, target_name = target.rsplit(".", 1)

    # construct relative path from current doc page to target page
    relative_segments_to_root = [".." for _ in current_doc.split("/")]
    relative_segments_to_target = target_module.split(".")

    # example full relative path: ../../../../../api/uncountable/types/identifier_t/#uncountable.types.identifier_t.IdentifierKey
    full_relative_path = "/".join([
        *relative_segments_to_root,
        autoapi_root,
        *relative_segments_to_target,
        f"#{target}",
    ])

    return nodes.reference(
        text=target_name if python_use_unqualified_type_names else target,
        children=[contnode],
        refuri=full_relative_path,
    )


def setup(app: Sphinx) -> None:
    app.connect("missing-reference", _hook_missing_reference)
