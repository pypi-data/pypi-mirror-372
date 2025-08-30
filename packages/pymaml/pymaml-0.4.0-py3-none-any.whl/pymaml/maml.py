"""
Main maml object.
"""

import warnings
from dataclasses import dataclass, asdict
import os

import yaml
from yaml import SafeDumper
from astropy.io.votable.ucd import check_ucd

from .parse import (
    today,
    is_valid,
    is_iso8601,
    RECOMENDED_META_DATA,
    OPTIONAL_META_DATA,
    MAML_KEY_ORDER,
    FIELD_KEY_ORDER,
    RECOMENDED_FIELD_META_DATA,
    REQURED_FIELD_META_DATA,
    OPTIONAL_FIELD_META_DATA,
)
from .read import read_maml


@dataclass
class Field:
    """
    Class storing the field data
    """

    name: str
    data_type: str
    unit: str = None
    info: str = None
    ucd: str = None
    array_size: int = None

    def __post_init__(self):
        if self.ucd is not None:
            if not check_ucd(self.ucd, check_controlled_vocabulary=True):
                raise AttributeError(f"{self.ucd} is not valid ucd.")

    @classmethod
    def from_dict(cls, dictionary: dict[str, str]):
        """
        Constructs a field object from a dictionary.
        """
        value = cls(name=None, data_type=None)
        for req in REQURED_FIELD_META_DATA:
            if req in dictionary:
                setattr(value, req, dictionary[req])
            else:
                raise ValueError(f"{req} missing for a valid Field entry.")

        for rec in RECOMENDED_FIELD_META_DATA:
            if rec in dictionary:
                setattr(value, rec, dictionary[rec])
            else:
                warnings.warn(
                    f"Recomended property '{rec}' not in dictionary for {dictionary["name"]} field"
                )

        for opt in OPTIONAL_FIELD_META_DATA:
            if opt in dictionary:
                setattr(value, opt, dictionary[opt])

        try:
            ucd = dictionary["ucd"]
            if not check_ucd(ucd, check_controlled_vocabulary=True):
                raise AttributeError(f"{ucd} is not valid ucd")
            value.ucd = ucd
        except KeyError:
            pass

        return value


@dataclass
class MAML:
    """
    Class for storing maml data.
    """

    table: str
    author: str
    fields: list[Field]
    survey: str = None
    dataset: str = None
    version: str = "0.1.0"
    date: str = today()
    coauthors: list[str] = None
    depends: list[str] = None
    description: str = None
    comments: list[str] = None

    @classmethod
    def from_file(cls, file_name: str) -> None:
        """
        Creates a MAML object from file.
        """
        dictionary = read_maml(file_name)
        if not is_valid(dictionary):
            raise AttributeError(f"{file_name} is not a valid maml file.")

        fields = [Field.from_dict(field) for field in dictionary["fields"]]
        value = cls(
            table=dictionary["table"], author=dictionary["author"], fields=fields
        )

        for recommended in RECOMENDED_META_DATA:
            if recommended in dictionary:
                setattr(value, recommended, dictionary[recommended])
            else:
                warnings.warn(f"Recommended value {recommended} not found in file.")

        for optional in OPTIONAL_META_DATA:
            if optional in dictionary:
                setattr(value, optional, dictionary[optional])

        return value

    def to_dict(self) -> dict[str, str]:
        """
        Dictionary representation of the MAML class.
        """
        raw_dictionary = asdict(self)
        ordered_fields = []
        for field in raw_dictionary["fields"]:
            ordered_fields.append({key: field[key] for key in FIELD_KEY_ORDER})
        raw_dictionary["fields"] = ordered_fields
        ordered_dictionary = {key: raw_dictionary[key] for key in MAML_KEY_ORDER}
        return ordered_dictionary

    def to_file(self, file_name: str) -> None:
        """
        Writes the current fields as valid maml.
        """
        SafeDumper.add_representer(
            type(None),
            lambda dumper, _: dumper.represent_scalar("tag:yaml.org,2002:null", ""),
        )
        root, ext = os.path.splitext(file_name)
        if ext != ".maml":
            raise ValueError(f"Extension '{ext}' is not a valid maml extension.")
        with open(f"{root}.maml", "w", encoding="utf8") as file:
            yaml.safe_dump(
                self.to_dict(), file, sort_keys=False, default_flow_style=False
            )

    @classmethod
    def default(cls):
        """
        Creates a default implementation.
        """
        return cls(
            table="Table Name",
            survey="Survey Name",
            dataset="Dataset Name",
            version="0.0.1",
            date="1995-12-09",
            author="Lead Author <email>",
            coauthors=["Co-Author 1 <email1>", "Co-Author 2 <email2>"],
            depends=[
                "Dataset 1 depends on [optional]",
                "Dataset 2 depends on [optional]",
            ],
            description="A couple sentences about the table.",
            comments=["Something 1", "Something 2"],
            fields=[
                Field("RA", "float", "deg", "Right Ascension", "pos.eq.ra"),
                Field("Dec", "float", "deg", "Declination", "pos.eq.dec"),
            ],
        )

    def add_field(
        self,
        name: str,
        data_type: str,
        unit: str = None,
        info: str = None,
        ucd: str = None,
        array_size: int = None,
    ):
        """
        Helper method to add a new field.
        """
        validated_field = Field(
            name=name,
            data_type=data_type,
            unit=unit,
            info=info,
            ucd=ucd,
            array_size=array_size,
        )
        self.fields.append(validated_field)

    def add_comment(self, comment: str):
        """
        Helper method to add comments
        """
        self.comments.append(str(comment))

    def set_date(self, date: str) -> None:
        """
        Helper method which sets the date if it is in the correct format.
        """
        if not is_iso8601(date):
            raise ValueError(f"'{date}' is not in ISO8601 format")
        self.date = date
