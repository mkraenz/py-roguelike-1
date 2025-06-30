import os
import urllib.request

dir = "C:/Users/RUNNER~1/AppData/Local/Nuitka/Nuitka/Cache/DOWNLO~1/depends/x86_64/"
# dir = "src/"
zip_filename = f"{dir}depends22_x64.zip"

urllib.request.urlretrieve(
    "https://www.dependencywalker.com/depends22_x64.zip",
    zip_filename,
)
print(f"Downloaded file to {zip_filename}")
error_code = os.system(
    f"powershell -command \"Expand-Archive -Force '{zip_filename}' 'C:/Users/RUNNER~1/AppData/Local/Nuitka/Nuitka/Cache/DOWNLO~1/depends/x86_64'\""
)
if error_code != 0:
    raise SystemExit("Installation of Dependency Walker on windows failed.")
print("Extracted dependency runner")
