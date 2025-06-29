import os

os_name = os.name
print(f"Running on {os_name}")
if os_name == "posix":
    os.system("cp -r assets dist/tstt_rl/assets")
elif os_name == "win32":
    # /i creates the missing destination directories, /s makes it recursive
    os.system("xcopy assets dist\tstt_rl\assets /s /i")
else:
    print(
        "Can only copy on linux and windows currently. Need to test for macOS (os_name =='darwin')"
    )
    raise SystemExit(1)

print("Copied assets directory")
