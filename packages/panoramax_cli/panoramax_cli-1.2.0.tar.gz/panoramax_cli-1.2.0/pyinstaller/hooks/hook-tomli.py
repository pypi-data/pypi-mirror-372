from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

binaries = collect_dynamic_libs("tomli", search_patterns=["*.dll", "*.so", "*.pyd"]) + collect_dynamic_libs(
    "5bae8a57b5ef85818b48__mypyc", search_patterns=["*.dll", "*.so", "*.pyd"]
)
hiddenimports = ["tomli", "5bae8a57b5ef85818b48__mypyc"]
