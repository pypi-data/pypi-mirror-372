
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""
import platform

import nanosurf.lib.util.dataexport as dataexport
import nanosurf.lib.util.fileutil as fileutil
if platform.version() != "Nanosurf_Linux":
    import nanosurf.lib.util.nhf_reader as nhf_reader
    import nanosurf.lib.util.nid_reader as nid_reader
    import nanosurf.lib.util.gwy_export as gwy_export


