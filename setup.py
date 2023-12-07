# import sys
# from cx_Freeze import setup, Executable

# build_exe_options = {
#     "packages": ["os", "pygame"],
#     "include_files": ["assets/"]
# }

# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

# setup(
#     name = "Shrubbery Quest",
#     version = "1.0",
#     description = "Shrubbery Quest, the best competitive platforming game",
#     options = {"build_exe": build_exe_options},
#     executables = [Executable("gameHandler.py", base=base, icon="assets/exe-logo.ico", target_name="Shrubbery Quest.exe")]
# )

# To make exe:
# uncomment code above

# create virtual env
# path/to/python3.11.7 -m venv venv

# activate env
# venv/scripts/activate

# pip install modules:
# pip install pygame requests ntplib cx_Freeze

# create exe build:
# python setup.py build