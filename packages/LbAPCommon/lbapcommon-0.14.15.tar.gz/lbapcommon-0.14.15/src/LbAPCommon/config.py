###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

known_working_groups = [
    "B2CC",
    "B2OC",
    "BandQ",
    "BnoC",
    "Calib",
    "Calo",
    "Charm",
    "DPA",
    "FlavourTagging",
    "HLT",
    "IFT",
    "Luminosity",
    "OpenData",
    "PID",
    "QCD",
    "QEE",
    "RD",
    "RTA",
    "Simulation",
    "SL",
    "Tracking",
]

known_data_types = ["Upgrade", "2011", "2012", "2015", "2016", "2017", "2018"]

known_input_types = ["DST", "MDST"]

allowed_priorities = ["1a", "1b", "2a", "2b"]

validation_types = [
    "duplicate_inputs",  # FIXME this cannot be used until a full job list is provided by exec-info
    "both_polarities_used",
    "job_name_matches_polarity",
    "event_stats",
]
default_validations = [
    "job_name_matches_polarity",
    "event_stats",
]

validation_modes = ["Strict", "Lenient", "Ignore"]
