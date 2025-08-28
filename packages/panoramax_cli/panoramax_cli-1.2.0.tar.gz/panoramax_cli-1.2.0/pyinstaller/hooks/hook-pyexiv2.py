# pyinstaller hook to find all pyexiv2 libraries
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Collect the required binary files
binaries = collect_dynamic_libs("pyexiv2", search_patterns=["*.dll", "*.so", "*.pyd"])

# Collect any data files if needed
datas = collect_data_files("pyexiv2")
