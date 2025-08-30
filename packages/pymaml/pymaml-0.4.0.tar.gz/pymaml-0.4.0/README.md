# pymaml
Official python package for reading, writing, and parsing the Meta yAML format. 

(see also https://github.com/asgr/MAML)

# MAML

MAML is a YAML based metadata format for tabular data (roughly implying Metadata yAML). This package is the official python interface to help read, write, and parse MAML files.

## Why MAML? 
We have VOTable and FITS header already?! Well, for various projects we were keen on a rich metadata format that was easy for humans and computers to both read and write. VOTable headers are very hard for humans to read and write, and FITS is very restrictive with its formatting and only useful for FITS files directly. In comes YAML, a very human and machine-readable and writable format. By restricting ourselves to a narrow subset of the language we can easily describe fairly complex table metadata (including all IVOA information). Introducing Meta yAML (MAML).

The MAML format files should be saved as example.maml etc. And the idea is the maml string can be inserted directly into a number of different file formats that accept key-value metadata (like Apache Arrow Parquet files). In the case of Parquet files they should be written to a 'maml' extension in the metadata section of the file.

## MAML Metadata Format

The MAML metadata format is a structured way to describe datasets, surveys, and tables using YAML. This format ensures that all necessary information about the data is captured in a clear and organized manner.

### Structure

The superset of allowed entries for MAML is below. Not all are required, but if present they should obey the order and naming.

- **survey**: The name of the survey. *Scalar string*. **[optional]**
- **dataset**: The name of the dataset. *Scalar string*. **[recommended]**
- **table**: The name of the table. *Scalar string*. **[required]**
- **version**: The version of the dataset. *Scalar string, integer or float*. **[required]**
- **date**: The date of the dataset in `YYYY-MM-DD` format. *Scalar string*. **[required]**
- **author**: The lead author of the dataset, including their email. *Scalar string*. **[required]**
- **coauthors**: A list of co-authors, each with their email. *Vector string*. **[optional]**
- **depends**: A list of datasets that this dataset depends on. *Vector string*. **[optional]**
- **description**: A sentence or two describing the table. *Scalar string*. **[recommended]**
- **comments**: A list of comments or interesting facts about the data. *Vector string*. **[optional]**
- **fields**: A list of fields in the dataset, each with the following attributes: **[required]**
  - **name**: The name of the field. *Scalar string*. **[required]**
  - **unit**: The unit of measurement for the field (if applicable). *Scalar string*. **[recommended]**
  - **info**: A short description of the field. *Scalar string*. **[recommended]**
  - **ucd**: Unified Content Descriptor for IVOA (can have many). *Vector string*. **[recommended]**
  - **data_type**: The data type of the field (e.g., `int32`, `string`, `bool`, `double`). *Scalar string*. **[required]**
  - **array_size**: Maximum length of character strings. *Scalar integer* or *Scalar string*. **[optional]**

This metadata format can be used to document datasets in a standardised way, making it easier to understand and share data within the research community. By following this format, you ensure that all relevant information about the dataset is captured and easily accessible.

This format contains the superset of metadata requirements for IVOA, Data Central and surveys like GAMA and WAVES.

If producing a maximal MAML then the metadata can be considered a MAML-Whale, and if only containing the required minimum entries it would be a MAML-Mouse. Between these two extremes you can choose your mammal of interest to reflect the quality/quantity of metadata. The sweet spot is obviously a MAML-Honey-Badger.


# pymaml
## Installation
pymaml can be installed easily with `pip`
```python
pip install pymaml
```

## Creating a new .maml file.

## Reading in a .maml file.
Reading a maml file is easily done using the `MAML` object in pymaml. Reading it in this way will include validation "for free". 
```python
from pymaml import MAML
new_maml = MAML.from_file("example.maml")

```
This MAML object will only be created if all the the required fields are present in the maml file.  


## Validating a .maml file.
The pymaml package has a `validate` function that will audit a .maml file and return weather or not that file is valid as well as describe why it isnt valid and any warnigns that the users might wish to consider.

```python
from pymaml import validate
validate("example.maml")

```

## Creating a new maml file
The `MAML` object is the core object for building and writing maml formats and will do all validation. Using this method **guarantees that the maml written is valid maml** including ucd checking and date formats.

At the very least, a table name, author name, and at least one Field need to be passed:
```python
from pymaml.maml import MAML, Field
new_maml = MAML(table="New table Name", Author="Me, myself, and I", fields = [Field(name='ra', data_type='float')])

```

The `Field` object is the main way to build new fields and will also force checks to make sure that the fields are valid.

For convience, a default maml construction can be built quickly with the class method `.default()`

```python
from pymaml import MAML
default_maml = MAML.default()

```
Values can be updated in the normal way in python classes. Or, for convience, several setter methods are available to use including `add_comment()`, `add_field()`, and `set_date()`

```python
from pymaml import MAML
maml = MAML.default()

maml.set_date("2025-01-02")
maml.add_field(Field(name="Declination", ucd="pos.eq.dec", data_type="float"))
maml.add_comment("This is an easy way to add a comment to the existing maml.")

```

Once the `MAML` object is built, then it can easily be written to file:
```python
maml.to_file("new_maml.maml")

```
