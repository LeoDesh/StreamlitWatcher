from pathlib import Path

# from garmin.utils.misc import split_lines_with_comma


def validate_file_type(file: Path) -> bool:
    if not file.is_file():
        return False
    if file.suffix != ".csv":
        return False
    return True


def validate_structure_of_csv_file(file: Path) -> bool:
    with open(str(file), "r", encoding="utf-8") as f:
        lines = [line for line in f.readlines()]
        if not check_for_valid_container(lines):
            return False
        return analyze_lines(lines)


def analyze_lines(lines: list[str], sep=",") -> bool:
    line_sizes = [len(list(line.split(sep))) for line in lines]
    return all(x == line_sizes[0] for x in line_sizes)


def check_for_valid_container(container: list | tuple | set):
    if not container:
        return False
    if (
        isinstance(container, list)
        or isinstance(container, tuple)
        or isinstance(container, set)
    ):
        return True
    return False


def validate_csv_file(file: Path) -> bool:
    validators = [
        (validate_file_type, "Wrong File Type"),
        (
            validate_structure_of_csv_file,
            "Not all Lines have the same elements, concerning the seperator ','.",
        ),
    ]
    for validator, err_msg in validators:
        if not validator(file):
            raise ValueError(err_msg)
    return True
