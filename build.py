import PyInstaller.__main__
from pathlib import Path

ENTRY = "dota2.py"
NAME = "OpenDota2Vision"
ICO_ICON = "icon.ico"
PNG_ICON = "icon.png"

def add_data_arg(src, dest="."):
    sep = ";" if (Path().anchor or "\\") else ":"
    return f"{src}{sep}{dest}"

args = [
    ENTRY,
    "--onefile",
    "--noconsole",
    f"--name={NAME}",
    f"--icon={ICO_ICON}",
    f"--version-file=file_version_info.txt",
    "--noconfirm",
    "--clean",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=customtkinter",
    "--hidden-import=customtkinter.windows",
    "--hidden-import=customtkinter.windows.widgets",
    "--hidden-import=customtkinter.windows.ctk_button",
    "--hidden-import=customtkinter.windows.ctk_label",
    "--hidden-import=customtkinter.windows.ctk_frame",
    "--hidden-import=customtkinter.windows.ctk_checkbox",
    "--hidden-import=customtkinter.windows.ctk_entry",
    "--hidden-import=pytesseract",
    "--hidden-import=requests",
    "--hidden-import=urllib3",
    "--hidden-import=certifi",
    "--hidden-import=charset_normalizer",
    "--hidden-import=idna",
    f"--add-data={add_data_arg(PNG_ICON, '.')}",
]


if __name__ == "__main__":
    PyInstaller.__main__.run(args)
