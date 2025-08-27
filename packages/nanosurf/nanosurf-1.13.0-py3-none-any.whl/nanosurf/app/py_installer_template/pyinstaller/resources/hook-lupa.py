#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = collect_data_files('lupa', excludes=["**/__pycache__"], include_py_files=True)
binaries = collect_dynamic_libs('lupa', search_patterns=['*.pyd'])
# print("******* LUPA start ****************************************************************************")
# print(datas)
# print(binaries)
# print("******* LUPA end ****************************************************************************")
