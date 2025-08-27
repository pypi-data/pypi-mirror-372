from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('nanosurf.lib', includes=["**/*"], excludes=["**/__pycache__"], include_py_files=False)
