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


def look_for_file_in_folder(folder: Path, file_stem: str) -> Path | None:
    for file in folder.iterdir():
        file_name_suffix = get_page_part(file)
        if file_name_suffix == file_stem and file.suffix == ".py":
            return file
    return None


def split_page_name(file_name: str) -> tuple[int, str]:
    idx, *_, page_name = file_name.split("__")
    return (int(idx), page_name)


def get_page_part(file_path: Path) -> str:
    return file_path.stem.split("__")[-1]


def get_folders(path: Path) -> list[Path]:
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_section_folder_mapping(view_folder: Path) -> dict[str, Path]:
    folder_dict = {}
    for folder_path in get_folders(view_folder):
        idx, section_name = split_page_name(folder_path.name)
        folder_dict[idx] = (section_name, folder_path)
    sorted_folder_dict = dict(sorted(folder_dict.items()))
    return {
        section_name: folder for (section_name, folder) in sorted_folder_dict.values()
    }


def extract_order_number_from_page(file: Path) -> int:
    index, *_ = file.stem.split("__")
    return int(index)
