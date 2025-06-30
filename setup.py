from cx_Freeze import setup

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "include_files": [("src/assets/", "assets/")],
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
