from pathlib import Path

import pytest

from garmin.utils.path_utils import (
    get_folders,
    get_relative_file_path,
    get_section_folder_mapping,
    look_for_page_in_folder,
    split_page_name,
)


@pytest.mark.path_utils
def test_get_relative_file_path_full_path(get_test_path: Path):
    file = get_test_path / "views" / "1__Running" / "1__running.py"
    full_file_path = file.resolve()
    assert get_relative_file_path(full_file_path, get_test_path / "outside") == file


@pytest.mark.path_utils
def test_get_relative_file_path_shortened_path(get_test_path: Path):
    view_path = get_test_path / "views"
    file = view_path / "1__Running" / "1__running.py"
    full_file_path = file.resolve()
    assert (
        get_relative_file_path(full_file_path, view_path)
        == Path(*view_path.parts[-2:]) / "1__Running" / "1__running.py"
    )


@pytest.mark.path_utils
def test_look_for_page_in_folder_non_python_file(get_test_path: Path):
    view_path = get_test_path / "views"
    assert look_for_page_in_folder(view_path, "t") is None


@pytest.mark.path_utils
def test_look_for_page_in_folder_wrong_python_file_format(get_test_path: Path):
    example_path = get_test_path / "outside"
    with pytest.raises(ValueError, match="not enough values to unpack"):
        assert look_for_page_in_folder(example_path, "utils") is None


@pytest.mark.path_utils
def test_look_for_page_in_folder_python_file_correct_format(get_test_path: Path):
    running_path = get_test_path / "views" / "1__Running"
    assert (
        look_for_page_in_folder(running_path, "running")
        == running_path / "1__running.py"
    )


@pytest.mark.path_utils
def test_split_page_name_correct_file_path(get_test_path: Path):
    assert split_page_name(
        get_test_path / "views" / "1__Running" / "1__running.py"
    ) == (1, "running")


@pytest.mark.path_utils
def test_split_page_name_correct_file_str(get_test_path: Path):
    assert split_page_name(
        (get_test_path / "views" / "1__Running" / "1__running.py").stem
    ) == (1, "running")


@pytest.mark.path_utils
def test_split_page_name_correct_file_path_multiple_underscores(get_test_path: Path):
    assert split_page_name(
        (get_test_path / "views" / "1__Running" / "2__running__distance.py").stem
    ) == (2, "distance")


@pytest.mark.path_utils
def test_split_page_name_incorrect_file_str(get_test_path: Path):
    with pytest.raises(ValueError, match="invalid literal for"):
        assert split_page_name(get_test_path / "outside" / "x__t.txt")


@pytest.mark.path_utils
def test_get_folders(get_test_path: Path):
    folders = [folder.stem for folder in get_folders(get_test_path / "views")]
    assert folders == ["1__Running", "2__Steps"]


@pytest.mark.path_utils
def test_get_section_folder_mapping(get_test_path: Path):
    assert get_section_folder_mapping(get_test_path / "views") == {
        "Running": get_test_path / "views" / "1__Running",
        "Steps": get_test_path / "views" / "2__Steps",
    }
