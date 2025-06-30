import os
import urllib.request

dir = "C:\\Users\\RUNNER~1\\AppData\\Local\\Nuitka\\Nuitka\\Cache\\DOWNLO~1\\depends\\x86_64\\"

urllib.request.urlretrieve(
    "https://www.dependencywalker.com/depends22_x64.zip",
    f"{dir}depends22_x64.zip",
)
os.system(
    "powershell -command \"Expand-Archive -Force 'C:\\Users\\RUNNER~1\\AppData\\Local\\Nuitka\\Nuitka\\Cache\\DOWNLO~1\\depends\\x86_64\\depends22_x64.zip' 'C:\\Users\\RUNNER~1\\AppData\\Local\\Nuitka\\Nuitka\\Cache\\DOWNLO~1\\depends\\x86_64'\""
)
print("Extracted dependency runner")
