import re
import sys


# Helper function that parses the filename.
# Expects sys.argv[1] to be of the form \c PLC<num>_<name>_HM.pmc
# \return (num, name, filename)
def parse_args():
    # find the plc number and name from the filename
    filename = sys.argv[1]
    result = re.search(r"PLC(\d+)_(.*)_HM\.pmc", filename)
    if result is not None:
        num, name = result.groups()
    else:
        sys.stderr.write(
            "***Error: Incorrectly formed homing plc filename: %s\n" % filename
        )
        sys.exit(1)
    return int(num), name, filename
