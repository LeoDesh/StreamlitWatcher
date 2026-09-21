from pathlib import Path


def get_relative_file_path(file_dunder: str, relative_folder_path: Path) -> Path:
    """Returns path of given file, relative to the project, if it is found within the views folder
    Args:
        str: dunder file (__file__)
        path: relative_folder_path
    Returns:
        Path: abbrevated file path
    Example:
        relative_folder_path: views: ...projects/python/garmin/views/1__Running/1__running.py ->  garmin/views/1__Running/1__running.py
        relative_folder_path: views: ...projects/python/garmin/charts/config.py ->  ...projects/python/garmin/charts/config.py
        relative_folder_path: garmin: ...projects/python/garmin/charts/config.py ->  ...python/garmin/charts/config.py
    """
    path = Path(file_dunder).resolve()
    path_parts = path.parts
    view_folder_name = relative_folder_path.name
    project_folder_name = relative_folder_path.parent.name
    if view_folder_name in path_parts and project_folder_name in path_parts:
        idx = path_parts.index(project_folder_name)
        return Path(*path_parts[idx:])
    return path


def look_for_page_in_folder(folder: Path, searched_page: str) -> Path | None:
    """Returns None or first file found, whose page name coincides with the searched page"""
    for file in folder.iterdir():
        page_name = get_page_name(file)
        if page_name == searched_page and file.suffix == ".py":
            return file
    return None


def split_page_name(file: str | Path) -> tuple[int, str]:
    """Splits file into index and page name
    Returns:
            tuple[int,str]: Index and Page Name of provided file
    Example:
        Path("1__running.py") -> [1,"running"]

        "1__running" -> [1,"running"]

        Path("2__running__distance.py") -> [2,"distance"]

        "2__running__distance.py" -> [2,"distance"]
    """
    file_name = file if isinstance(file, str) else file.stem
    idx, *_, page_name = file_name.split("__")
    return (int(idx), page_name)


def get_page_name(file_path: Path) -> str:
    """Returns Page Name of given file"""
    _, page_name = split_page_name(file_path)
    return page_name


def get_folders(dir_path: Path) -> list[Path]:
    """Returns list of folders in the given directory path"""
    return [folder for folder in dir_path.iterdir() if folder.is_dir()]


def get_section_folder_mapping(view_folder: Path) -> dict[str, Path]:
    """Returns sorted sections and corresponding folder from provided view directory"""
    folder_dict = {}
    for folder_path in get_folders(view_folder):
        idx, section_name = split_page_name(folder_path)
        folder_dict[idx] = (section_name, folder_path)
    sorted_folder_dict = dict(sorted(folder_dict.items()))
    return {
        section_name: folder for (section_name, folder) in sorted_folder_dict.values()
    }


def extract_order_number_from_page(file: Path) -> int:
    """Returns Sort Number for given file"""
    index, _ = split_page_name(file)
    return index
