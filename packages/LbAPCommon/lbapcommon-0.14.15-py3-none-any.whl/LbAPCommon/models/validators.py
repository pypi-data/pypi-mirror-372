###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import re
from typing import Any


def output_filetype_validator(v: str) -> str:
    # Normalize the filetype to uppercase
    v = v.upper()
    if re.findall(r"[0-9]{8}", v, re.IGNORECASE):
        raise ValueError("It appears the event type is included. Please remove it!")
    if re.findall(r"Mag(Up|Down)", v, re.IGNORECASE):
        raise ValueError(
            "It appears the magnet polarity is included. Please remove it!"
        )
    if re.findall(r"(^|[^0-9])20(1|2)[12345678]($|[^0-9])", v, re.IGNORECASE):
        raise ValueError(
            "It appears the data taking year is included. Please remove it!"
        )
    return v


def force_to_list(v: Any):
    # Normalise list/str fields to always be lists
    if not isinstance(v, (list, dict)):
        return [v]
    return v
