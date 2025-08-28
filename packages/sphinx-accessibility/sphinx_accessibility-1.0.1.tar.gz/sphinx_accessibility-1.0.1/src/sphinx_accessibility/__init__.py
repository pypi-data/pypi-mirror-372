# -*- coding: utf-8 -*-
"""
sphinx_accessibility
~~~~~~~~~~~~~~~~~~~~

Sphinx extension that provides accessibility features.

"""

import os

from sphinx.application import Sphinx
from typing import Any, Dict, Set, Union, cast
from pathlib import Path
from sphinx.util.fileutil import copy_asset
from sphinx.locale import get_translation

MESSAGE_CATALOG_NAME = "accessibility"
translate = get_translation(MESSAGE_CATALOG_NAME)

def setup(app: Sphinx) -> Dict[str, Any]:
    
    app.connect("builder-inited", set_asset_files)  # event order - 2
    app.connect("build-finished", copy_asset_files)  # event order - 16

    # add translations
    package_dir = os.path.abspath(os.path.dirname(__file__))
    locale_dir = os.path.join(package_dir, "translations", "locales")
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def set_asset_files(app: Sphinx) -> None:
    """Sets the asset files for the codex extension"""

    app.add_js_file(None, body=f"let enableFont = '{translate('Enable')}';")
    app.add_js_file(None, body=f"let disableFont = '{translate('Disable')}';")
    app.add_js_file(None, body=f"let enableContrast = '{translate('Enable high contrast')}';")
    app.add_js_file(None, body=f"let disableContrast = '{translate('Disable high contrast')}';")

    app.add_js_file("Accessibility.js")
    app.add_css_file("HighContrast.css")
    app.add_css_file("OpenDyslexic.css")
    app.add_css_file("SVGstyling.css")

def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    """Copies required assets for formating in HTML"""

    html_assets_dir = Path(__file__).parent.joinpath("assets", "html").absolute()
    asset_files = list(html_assets_dir.glob("*"))
    if exc is None:
        for path in asset_files:
            copy_asset(str(path), str(Path(app.outdir).joinpath("_static").absolute()))