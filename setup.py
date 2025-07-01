import platform

from cx_Freeze import setup

included_files = (
    [("src/assets/", "assets/")]
    if platform.system == "Linux"
    else [("src/assets/", "assets/"), ("SDL3.dll", "SDL3.dll")]
)

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "include_files": included_files,
    "excludes": ["tkinter", "unittest", "tests"],
    "zip_include_packages": [
        "PyYAML",
        "tcod",
    ],
}

setup(
    name="tstt_rl",
    version="0.1",
    description="TypeScriptTeatime Roguelke",
    options={"build_exe": build_exe_options},
    executables=[{"script": "src/tstt_rl.py", "base": "gui"}],
    target_name="tstt_rl",
)
