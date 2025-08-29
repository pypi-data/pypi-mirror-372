###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

# pylint: disable=import-error
from GaudiConf.LbExec.options import FileFormats
from GaudiConf.LbExec.options import Options as OptionsBase

SUMMARY_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
    <success>True</success>
    <step>finalize</step>
    <usage><stat unit="KB" useOf="MemoryMaximum">0</stat></usage>
    <input>
{input_files}
    </input>
    <output>
{output_files}
    </output>
</summary>
"""
XML_FILE_TEMPLATE = '     <file GUID="" name="{name}" status="full">{n}</file>'
ALG_TO_CODE = {
    "ZLIB": 1,
    "LZMA": 2,
    "LZ4": 4,
    "ZSTD": 5,
}
POOL_XML_CATALOG_HACK_TEMPLATE = """<File ID="{uuid}">
   <physical>
      <pfn filetype="ROOT_All" name="{filename}"/>
   </physical>
   <logical/>
</File>
</POOLFILECATALOG>
"""


class Options(OptionsBase):
    """Fake wrapper around OptionsBase to remove things that don't make sense here."""

    input_type: FileFormats = FileFormats.ROOT
    simulation: None = False
    data_type: None = None


def read_xml_file_catalog(xml_file_catalog):
    """Lookup the LFN->PFN mapping from the XML file catalog."""
    if xml_file_catalog is None:
        return {}

    tree = ET.parse(xml_file_catalog)
    pfn_lookup: dict[str, list[str]] = {}
    for file in tree.findall("./File"):
        lfns = [x.attrib.get("name") for x in file.findall("./logical/lfn")]
        pfns = [x.attrib.get("name") for x in file.findall("./physical/pfn")]
        if len(lfns) > 1:
            raise NotImplementedError(lfns)
        if lfns:
            lfn = lfns[0]
        elif len(pfns) > 1:
            raise NotImplementedError(pfns)
        else:
            lfn = pfns[0]
        pfn_lookup[f"LFN:{lfn}"] = pfns
    return pfn_lookup


def resolve_input_files(input_files, file_catalog):
    """Resolve LFNs to PFNs using what was returned from read_xml_file_catalog."""
    resolved = []
    for input_file in input_files:
        if input_file.startswith("LFN:"):
            if input_file in file_catalog:
                print("Resolved", input_file, "to", file_catalog[input_file][0])
                input_file = file_catalog[input_file][0]
            else:
                raise ValueError(f"Could not resolve {input_file}: {file_catalog}")
        resolved.append(input_file)
    return resolved


def hadd(options: Options, compression: str = "ZSTD:4"):
    """Use had to merge ROOT files.

    This impersonates an lbexec-style application to merge ROOT files using hadd.
    The Gaudi event loop is never started and we write the output summary xml manually.
    """
    if os.environ.get("LBAPI_HACK_XML_FILE_CATALOG"):
        # Gaudi doesn't write an entry in pool_xml_catalog.xml for ntuple files.
        # LHCbDIRAC implicitly fixes this when uploading the output of the job
        # and downloading it into the merge job, however we need to do this manually
        # when running a local test.
        print("Hacking XML file catalog")
        orig_xml = Path(options.xml_file_catalog).read_text()
        if "</POOLFILECATALOG>" not in orig_xml:
            raise NotImplementedError(orig_xml)
        for lfn in options.input_files:
            if lfn.startswith("LFN:") and not lfn.startswith("LFN:/"):
                raw_lfn = lfn.split(":", 1)[1]
                print("Adding LFN", raw_lfn, "to", options.xml_file_catalog)
                fixed_xml = POOL_XML_CATALOG_HACK_TEMPLATE.format(
                    uuid=str(uuid.uuid4()), filename=raw_lfn
                )
        Path(options.xml_file_catalog).write_text(
            orig_xml.replace("</POOLFILECATALOG>", fixed_xml)
        )

    file_catalog = read_xml_file_catalog(options.xml_file_catalog)
    input_files = resolve_input_files(options.input_files, file_catalog)

    alg, level = compression.split(":")
    flags = [f"-f{ALG_TO_CODE[alg]}{int(level):02d}"]
    flags += ["-j", f"{options.n_threads}"]
    flags += ["-n", f"{max(10, options.n_threads*2)}"]

    with tempfile.NamedTemporaryFile(mode="wt") as tmpfile:
        tmpfile.write("\n".join(input_files))
        tmpfile.flush()
        cmd = ["hadd"] + flags + [options.ntuple_file, f"@{tmpfile.name}"]
        print("Running", cmd)
        subprocess.run(cmd, check=True)

    summary_xml = SUMMARY_XML_TEMPLATE.format(
        input_files="\n".join(
            XML_FILE_TEMPLATE.format(
                name=name if name.startswith("LFN:") else f"PFN:{name}", n=1
            )
            for name in options.input_files
        ),
        output_files=XML_FILE_TEMPLATE.format(
            name=f"PFN:{options.ntuple_file}", n=len(input_files)
        ),
    )
    if options.xml_summary_file:
        print("Writing XML summary to", options.xml_summary_file)
        Path(options.xml_summary_file).write_text(summary_xml)

    print("All done")
    sys.exit(0)
