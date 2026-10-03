from pathlib import Path


def validate_file_type(file: Path) -> bool:
    if not file.is_file():
        return False
    return file.suffix == ".csv"


def validate_file_structure(file: Path) -> bool:
    with open(str(file), "r", encoding="utf-8") as f:
        lines = f.readlines()
        return analyze_lines(lines)


def analyze_lines(lines: list[str], sep: str = ",") -> bool:
    if not lines:
        return False
    line_sizes = [len(list(line.split(sep))) for line in lines]
    return all(x == line_sizes[0] for x in line_sizes)


def validate_activities_file(file: Path) -> bool:
    validators = [
        (validate_file_type, "Wrong File Type"),
        (
            validate_file_structure,
            "Not all Lines have the same elements, concerning the seperator ','.",
        ),
    ]
    for validator, err_msg in validators:
        if not validator(file):
            raise ValueError(err_msg)
    return True
