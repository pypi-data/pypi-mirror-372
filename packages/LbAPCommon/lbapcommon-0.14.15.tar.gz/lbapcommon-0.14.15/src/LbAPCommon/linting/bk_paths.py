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

__all__ = ("validate_bk_query", "InvalidBKQueryError")

import os


class InvalidBKQueryError(ValueError):
    """Exception raise by validate_bk_query if the BK query is invalid."""


def validate_bk_query(bk_query):
    """Perform a cursory check that the BK path is sane.

    Args:
        bk_query (str): BKQuery string.

    Raises:
        InvalidBKQueryError: The BKQuery is not valid.

    Returns:
        bool: True if the BKQuery is valid.
    """
    message = "The provided BK query is not valid!\n\n"

    # Make a dict of the query parts
    mydict = _buildBKQuery(bk_query)

    # Check the EventType is there, is an integer and has 8 digits
    eventtype = mydict.get("EventType")
    if not isinstance(eventtype, int) or len(str(eventtype)) != 8:
        # The most common mistake is to have the EventType in the ConditionDescription,
        # with the ConditionDescription ending up in the ProcessingPass.
        if len(str(mydict.get("ConditionDescription", ""))) == 8:
            message += "Found EventType in ConditionDescription - "
            message += "the EventType must go at the end of the query!"

            mydict["EventType"] = mydict["ConditionDescription"]
            new_cond = mydict["ProcessingPass"].split("/")[1]
            mydict["ConditionDescription"] = new_cond
            mydict["ProcessingPass"] = mydict["ProcessingPass"].replace(
                "/" + new_cond, ""
            )
            new_ft = mydict["ProcessingPass"].split("/")[-1]
            mydict["FileType"] = new_ft
            mydict["ProcessingPass"] = mydict["ProcessingPass"].replace(new_ft, "")
            # Now assemble the query
            retPath = "/"
            for v in mydict.values():
                retPath = os.path.join(retPath, *v.split("/"))
            message += f"\n\nSuggested BK path: {retPath}"
        raise InvalidBKQueryError(message)

    if mydict.get("FileType") == "RAW":
        message += "It is not possible to run over RAW data by default. "
        message += "Please use Stripping/Sprucing output instead.\n\n"
        message += "If the regular output is not usable for some reason "
        message += "contact the OPG to arrange a central production.\n\n"
        message += "If you think this is an erroneous restriction, "
        message += "please contact DPA-WP2."
        if "DEBUG_ALLOW_ALL_BK_PATHS" not in os.environ:
            raise InvalidBKQueryError(message)

    return True


def _buildBKQuery(bkPath=""):
    """Builds a dictionary from a BK path. Taken from LHCbDirac BKClient.

    Args:
        bkPath (str, optional): Bookkeeping path. Defaults to "".

    Raises:
        ValueError: BK path is invalid.

    Returns:
        dict: Result of the BKQuery.
    """
    bkQueryDict = {}

    if bkPath:
        bkFields = (
            "ConfigName",
            "ConfigVersion",
            "ConditionDescription",
            "ProcessingPass",
            "EventType",
            "FileType",
        )
        url = bkPath.split(":", 1)
        if len(url) == 1:
            bkPath = url[0]
        else:
            if url[0] == "evt":
                bkFields = (
                    "ConfigName",
                    "ConfigVersion",
                    "EventType",
                    "ConditionDescription",
                    "ProcessingPass",
                    "FileType",
                )
            elif url[0] == "pp":
                bkFields = ("ProcessingPass", "EventType", "FileType")
            elif url[0] == "prod":
                bkFields = ("Production", "ProcessingPass", "EventType", "FileType")
            elif url[0] == "runs":
                bkFields = ("Runs", "ProcessingPass", "EventType", "FileType")
            elif url[0] not in ("sim", "daq", "cond"):
                raise ValueError("Invalid BK path:%s" % bkPath)
            bkPath = url[1]
        if bkPath[0] != "/":
            bkPath = "/" + bkPath
        if bkPath[0:2] == "//":
            bkPath = bkPath[1:]
        bkPath = bkPath.replace("RealData", "Real Data")
        i = 0
        processingPass = "/"
        defaultPP = False
        bk = bkPath.split("/")[1:] + len(bkFields) * [""]
        for bpath in bk:
            if bkFields[i] == "ProcessingPass":
                if (
                    bpath != ""
                    and bpath.upper() != "ALL"
                    and not bpath.split(",")[0].split(" ")[0].isdigit()
                ):
                    processingPass = os.path.join(processingPass, bpath)
                    continue
                # Set the PP
                if processingPass != "/":
                    bkQueryDict["ProcessingPass"] = processingPass
                else:
                    defaultPP = True
                i += 1
            if bkFields[i] == "EventType" and bpath:
                eventTypeList = []
                if bpath.upper() == "ALL":
                    bpath = "ALL"
                else:
                    for et in bpath.split(","):
                        try:
                            eventType = int(et.split(" ")[0])
                            eventTypeList.append(eventType)
                        except ValueError:
                            pass
                    if len(eventTypeList) == 1:
                        eventTypeList = eventTypeList[0]
                    bpath = eventTypeList
            # Set the BK dictionary item
            if bpath != "":
                bkQueryDict[bkFields[i]] = bpath
            if defaultPP:
                # PP was empty, try once more to get the Event Type
                defaultPP = False
            else:
                # Go to next item
                i += 1
            if i == len(bkFields):
                break

        # Set default event type to real data
        if bkQueryDict.get("ConfigName") != "MC" and not bkQueryDict.get("EventType"):
            bkQueryDict["EventType"] = "90000000"
        if bkQueryDict.get("EventType") == "ALL":
            bkQueryDict.pop("EventType")

    return bkQueryDict
