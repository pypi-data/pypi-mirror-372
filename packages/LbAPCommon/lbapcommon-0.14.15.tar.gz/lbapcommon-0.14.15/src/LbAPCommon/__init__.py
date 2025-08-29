###############################################################################
# (c) Copyright 2020-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

__all__ = [
    "get_api_token",
    "wipe_token_cache",
    "hacks",
    "render_yaml",
    "parse_yaml",
    "validate_yaml",
    "lint_all",
    "validators",
    "write_jsroot_compression_options",
]

from os.path import join

import jinja2

from LbAPCommon.models import parse_yaml

from . import hacks, validators
from .linting import lint_all


def render_yaml(raw_yaml):
    """Render a "raw" YAML jinja template.

    Accepts LbAP yaml configuration jinja template and renders it into a full YAML configuration.

    Args:
        raw_yaml (str): YAML jinja-template string

    Raises:
        ValueError: raised if jinja2 couldn't render the raw_yaml string.

    Returns:
        str: a jinja-rendered YAML string.
    """
    try:
        rendered_yaml = jinja2.Template(
            raw_yaml, undefined=jinja2.StrictUndefined
        ).render()
    except jinja2.TemplateError as e:
        raise ValueError(
            "Failed to render with jinja2 on line %s: %s"
            % (getattr(e, "lineno", "unknown"), e)
        ) from e
    return rendered_yaml


def validate_yaml(*_):
    """Validate YAML configuration for anything that would definitely break a job or the production.

    Args:
        jobs_data (dict): Parsed job configuration.
        repo_root (str): Repository location.
        prod_name (str): Production name.

    Raises:
        ValueError: Raised if there are showstopper issues in the parsed job configuration.
    """

    pass


def write_jsroot_compression_options(dynamic_dir):
    """Write options file to configure JSROOT-compatible compression on job output files.

    Args:
        dynamic_dir: Location to write the use-jsroot-compression.py options file.
    """
    with open(join(dynamic_dir, "use-jsroot-compression.py"), "wt") as fp:
        fp.write(
            "\n".join(
                [
                    "from Configurables import RootCnvSvc",
                    "RootCnvSvc().GlobalCompression = 'ZLIB:1'",
                    "",
                    "try:",
                    "    from Configurables import DaVinci",
                    "except ImportError:",
                    "    pass",
                    "else:",
                    "    try:",
                    "        DaVinci().RootCompressionLevel = 'ZLIB:1'",
                    "    except AttributeError:",
                    "        pass",
                ]
            )
        )
