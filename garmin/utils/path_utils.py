from pathlib import Path


def get_relative_file_path(
    file_dunder: str, relative_folder_path: Path, idx_shift: int = 0
) -> Path:
    """Returns path of given file, relative to the project, if it is found within the provided folder
    Args:
        str: dunder file (__file__)
        path: relative_folder_path
        idx_shift: skip folders within path
    Returns:
        Path: abbrevated file path
    Example:
        >>> get_relative_file_path("projects/python/garmin/views/1__Running/1__running.py",Path("views")):
        Path("garmin/views/1__Running/1__running.py")

        >>> get_relative_file_path("projects/python/garmin/charts/config.py",Path("views")):
        Path("projects/python/garmin/charts/config.py")

        >>> get_relative_file_path("projects/python/garmin/charts/config.py",Path("garmin")):
        Path("python/garmin/charts/config.py")

        >>> get_relative_file_path("projects/python/garmin/charts/config.py",Path("garmin"),idx_shift=2):
        Path("charts/config.py")
    """
    path = Path(file_dunder).resolve()
    path_parts = path.parts
    view_folder_name = relative_folder_path.name
    project_folder_name = relative_folder_path.parent.name
    if view_folder_name in path_parts and project_folder_name in path_parts:
        idx = path_parts.index(project_folder_name)
        return Path(*path_parts[idx + idx_shift :])
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
    Args:
        file (str): The path or name of the file to be split.
    Returns:
        tuple[int,str]: Index and Page Name of provided file
    Example:
        >>> split_page_name("1__running.py")
        (1,"running")

        >>> split_page_name(Path("2__running__distance.py"))
        (2,"distance")
    """
    file_name = file if isinstance(file, str) else file.stem
    idx, *_, page_name = file_name.split("__")
    return (int(idx), page_name)


def get_page_name(file_path: Path) -> str:
    """Returns the page name for the provided path

    Args:
        file_path (Path): path to the streamlit page
    Returns:
        str: page name
    Example:
        >>> get_page_name(Path("1__running.py"))
        "running"
    """
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
        section_name: folder_path
        for (section_name, folder_path) in sorted_folder_dict.values()
    }


def get_url_path(
    file: Path, relative_folder: Path, shift_idx: int = 2, use_hyphen: bool = True
) -> str:
    """Converts provided file path and the folder to abbrevate the path into a url str"""
    raw_url_path = get_relative_file_path(str(file), relative_folder, shift_idx)
    url_path = f"{raw_url_path.parent.stem}/{raw_url_path.stem}"
    return url_path.replace("/", "-") if use_hyphen else url_path


def extract_order_number_from_page(file: Path) -> int:
    """Returns Sort Number for given file"""
    index, _ = split_page_name(file)
    return index


def create_folder_if_not_exists(folder: Path) -> None:
    folder.mkdir(exist_ok=True)
