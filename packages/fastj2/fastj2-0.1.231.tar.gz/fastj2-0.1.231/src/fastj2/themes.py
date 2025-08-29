from pathlib import Path
from .html_render_error import render_error
from .html_header import header


def available_themes():
    themes = {}
    for each in THEME_DIR.glob("*"):
        path = Path(each)
        name = path.name
        themes[name] = path
    return themes


THEME_DIR = Path(__file__).parent / "themes"

THEMES = available_themes()

FILE_STRUCTURE = {
    "templates": {
        "html": {
            "header.html": header,
            "render_error.html": f"{render_error}",
            "content": {

            }
        },
        "js": {
        },
        "css": {
        }
    }
}


def file_structure(path: Path):
    top_level = {}
    for each in path.glob("*"):
        path = Path(each)
        name = path.name
        if "vars.css" in str(path):
            top_level["vars.css"] = path.read_text()
            continue
        else:
            top_level[name] = {}
            for file in path.glob("*"):
                filepath = Path(file)
                filename = filepath.name
                if filepath.is_file():
                    top_level[name][filename] = filepath.read_text()
                else:
                    continue
    return top_level


def choose_theme(theme: str):
    if theme in THEMES.keys():
        current_theme = file_structure(THEMES[theme])
    else:
        raise KeyError(f"Theme not found in {THEME_DIR}")
    file_struct = FILE_STRUCTURE
    file_struct["templates"]["css"] = current_theme
    return file_struct


if __name__ == "__main__":
    print(THEMES)
    print(choose_theme("basic"))
    # print(file_structure(Path("themes/basic")))
