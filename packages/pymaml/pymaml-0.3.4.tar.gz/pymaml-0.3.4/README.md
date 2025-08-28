# pymaml
Official python package for reading, writing, and parsing the Meta yAML format. 

(see also https://github.com/asgr/MAML)

MAML is a YAML based metadata format for tabular data. This package is a simple python interface to help read, validate and write MAML files.

## Why use MAML?
Why MAML? We have VOTable and FITS header already?! Well, for various projects we were keen on a rich metadata format that was easy for humans and computers to both read and write. VOTable headers are very hard for humans to read and write, and FITS is very restrictive with its formatting and only useful for FITS files directly. In comes YAML, a very human and machine readable and writable format. By restricting ourselves to a narrow subset of the language we can easily describe fairly complex table metadata (including all IVOA information). So this brings us to MAML: Metadata yAML.

MAML format files should be saves as example.maml etc. And the idea is the yaml string can be inserted directly into a number of different file formats that accept key-value metadata (like Apache Arrow Parquet files). In the case of Parquet files they should be written to a 'maml' extension in the metadata section of the file.

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