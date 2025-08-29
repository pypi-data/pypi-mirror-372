###############################################################################
# (c) Copyright 2020-2023 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import re

RE_COUNTER_ROW = (
    r"(^\s\|[\s\*]\"(?P<name>.*?)(\"\s*|)\|(?P<count>[0-9\.\%\(\)\+\-\se]+)\|((?P<sum>[0-9\.\%\(\)\+\-\se]+)\||)"
    r"((?P<meaneff>[0-9\.\%\(\)\+\- e]+)\||)((?P<rmserr>[0-9\.\%\(\)\+\-\se]+)\||)((?P<min>[0-9\.\%\(\)\+\-\-\se]+)\||)"
    r"((?P<max>[0-9\.\%\(\)\+\- e]+)\||)$\n)"
)
# Parses a single counter row of the block e.g.
#  |*"#accept"                                       |      1093 |       1093 |(  100.000 +- 0.0914913)%|   -------   |   -------   |

RE_COUNTER_BLOCK = (
    r"^(((.*?)UTC |)(?P<blockname>.*?)([\. ]+)(INFO|SUCCESS)\s+(Number of counters\s+:\s+(?P<Nctrs>\d+))"
    + r"$\s*^\s*\|\s+Counter\s+\|\s+#\s+\|\s+sum\s+\|\s+mean\/eff\^\*\s+\|\s+rms\/err\^\*\s+\|\s+min\s+\|\s+max\s+\|$\s*)("
    + RE_COUNTER_ROW
    + r")+"
)
# Parses an entire "block" containing counters emitted by a module into the log e.g. "StdLoosePi02gg"
# 2023-06-16 18:20:08 UTC StdLoosePi02gg    SUCCESS Number of counters : 5
#  |    Counter                                      |     #     |    sum     | mean/eff^* | rms/err^*  |     min     |     max     |
#  |*"#accept"                                       |      1093 |       1093 |(  100.000 +- 0.0914913)%|   -------   |   -------   |
#  | "Created resolved pi0"                          |     99028 |      99028 |     1.0000 |     0.0000 |      1.0000 |      1.0000 |
#  | "Created resolved pi0->(ee)(ee)"                |      9283 |       9283 |     1.0000 |     0.0000 |      1.0000 |      1.0000 |
#  | "Created resolved pi0->g(ee)"                   |     39806 |      39806 |     1.0000 |     0.0000 |      1.0000 |      1.0000 |
#  | "Created resolved pi0->gg"                      |     49939 |      49939 |     1.0000 |     0.0000 |      1.0000 |      1.0000 |

RE_FLAGS = re.IGNORECASE | re.MULTILINE
RE_ROW_PARSER = re.compile(RE_COUNTER_ROW, RE_FLAGS)
RE_FULL_COUNTER_PARSER = re.compile(RE_COUNTER_BLOCK, RE_FLAGS)


def parse_gaudi_log_counters(log_text: str):
    """Extract counters from a Gaudi application log."""
    counters = []

    for match in RE_FULL_COUNTER_PARSER.finditer(log_text):
        block = match.group(0)
        blockname = match.group("blockname")
        nctrs = int(match.group("Nctrs"))

        counter_block = [
            {k: v.strip() for k, v in rowmatch.groupdict().items() if v is not None}
            for rowmatch in RE_ROW_PARSER.finditer(block)
        ]
        counters.append(
            (
                blockname,
                counter_block,
            )
        )
        assert len(counter_block) == nctrs, (
            f"Number of parsed counters ({nctrs}) for {blockname}"
            " does not match number of counters specified in log"
            f" ({len(counter_block)})."
        )

    return counters
