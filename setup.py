# import sys
# from cx_Freeze import setup, Executable

# build_exe_options = {
#     "packages": ["os", "pygame"],
#     "include_files": ["assets/", "audioLevels.txt", "CurrentCharacter.txt", "currentLevel.txt", "MaxUnlocked.txt"]
# }

# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

# setup(
#     name = "Shrubbery Quest",
#     version = "1.0",
#     description = "Your Pygame application!",
#     options = {"build_exe": build_exe_options},
#     executables = [Executable("gameHandler.py", base=base, icon="assets/exe-logo.ico", target_name="Shrubbery Quest.exe")]
# )