"""
Helper module to parse and check valid maml data structures.
"""

import datetime
import os
import yaml
from rich.console import Console
from rich.text import Text
from astropy.io.votable.ucd import check_ucd

REQUIRED_META_DATA = ["table", "version", "date", "author", "fields"]
RECOMENDED_META_DATA = ["survey", "dataset"]
OPTIONAL_META_DATA = ["coauthors", "depend", "comment"]

REQURED_FIELD_META_DATA = ["name", "data_type"]
RECOMENDED_FIELD_META_DATA = ["unit", "description", "ucd"]
FIELD_KEY_ORDER = ["name", "unit", "description", "ucd", "data_type"]

MAML_KEY_ORDER = [
    "survey",
    "dataset",
    "table",
    "version",
    "date",
    "author",
    "coauthors",
    "depend",
    "comment",
    "fields",
]


def today() -> str:
    """
    Returns todays date in the correct iso format.
    """
    return datetime.date.isoformat(datetime.date.today())


def is_iso8601(date: str) -> bool:
    """
    Validates that the given date is in the ISO 8601 format (https://en.wikipedia.org/wiki/ISO_8601)
    """
    try:
        datetime.datetime.fromisoformat(date)
        return True
    except ValueError:
        return False


def is_valid(maml_data: dict[str:str]) -> bool:
    """
    Checks if the dict is a valid representation of maml data
    """
    if not isinstance(maml_data, dict):
        return False
    try:
        for required in REQUIRED_META_DATA:
            _ = maml_data[required]

        fields = maml_data["fields"]
        for field in fields:
            for required in REQURED_FIELD_META_DATA:
                _ = field[required]
    except KeyError:
        return False

    return is_iso8601(maml_data["date"])



console = Console()


def validate(file_path: str) -> dict:
    """
    Validate a .maml (YAML) file against the MAML schema.
    Prints a colored report using Rich.
    Returns a dict containing 'errors' and 'warnings'.
    """

    report = {"errors": [], "warnings": []}

    # --- Check extension ---
    _, ext = os.path.splitext(file_path)
    if ext not in (".maml", ".yml"):
        report["errors"].append(f"File extension {ext} is not valid (expected .maml)")
    elif ext == ".yml":
        report["warnings"].append("File uses .yml extension instead of .maml")

    # --- Try to load YAML ---
    try:
        with open(file_path, encoding='utf8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        report["errors"].append(f"YAML parsing error: {e}")
        data = None

    if not isinstance(data, dict):
        report["errors"].append("Top-level YAML is not a dictionary")
        data = {}

    # --- Check required metadata ---
    for key in REQUIRED_META_DATA:
        if key not in data:
            report["errors"].append(f"Missing required field: {key}")

    for key in RECOMENDED_META_DATA:
        if key not in data:
            report["warnings"].append(f"Missing recommended field: {key}")

    # --- Check date ---
    if "date" in data and not is_iso8601(data["date"]):
        report["errors"].append(f"Date '{data['date']}' is not ISO 8601 (YYYY-MM-DD)")

    # --- Check fields ---
    fields = data.get("fields", [])
    if not isinstance(fields, list) or not fields:
        report["errors"].append("`fields` must be a non-empty list")
    else:
        all_units_none = True
        for i, field in enumerate(fields, start=1):
            # required keys
            for req in REQURED_FIELD_META_DATA:
                if req not in field:
                    report["errors"].append(f"Field {i} missing required key: {req}")

            # recommended keys
            for rec in RECOMENDED_FIELD_META_DATA:
                if rec not in field:
                    report["warnings"].append(f"Field {i} missing recommended key: {rec}")

            # unit check
            if field.get("unit") not in (None, "", " "):
                all_units_none = False

            # UCD validation
            if "ucd" in field and field["ucd"] is not None:
                if not check_ucd(field["ucd"], check_controlled_vocabulary=True):
                    report["errors"].append(
                        f"Field {i} has invalid UCD: {field['ucd']}"
                    )

        if all_units_none:
            report["warnings"].append("All fields are missing `unit` values")

    # --- Print results ---
    for err in report["errors"]:
        console.print(Text(err, style="bold red"))

    for warn in report["warnings"]:
        console.print(Text(warn, style="yellow"))

    if report["errors"]:
        console.print(Text("NOT VALID", style="bold red"))
    elif report["warnings"]:
        console.print(Text("VALID (with warnings)", style="yellow"))
    else:
        console.print(Text("VALID", style="green"))

    return report
