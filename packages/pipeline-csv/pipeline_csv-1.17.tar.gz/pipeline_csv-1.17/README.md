# PipelineCsv library

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/vb64/pipeline.csv/pep257.yml?label=Pep257&style=plastic&branch=main)](https://github.com/vb64/pipeline.csv/actions?query=workflow%3Apep257)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/vb64/pipeline.csv/py3.yml?label=Python%203.8-3.13&style=plastic&branch=main)](https://github.com/vb64/pipeline.csv/actions?query=workflow%3Apy3)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/031838411159440885e8c4a28f233c4e)](https://app.codacy.com/gh/vb64/pipeline.csv/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/031838411159440885e8c4a28f233c4e)](https://app.codacy.com/gh/vb64/pipeline.csv/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

[In Russian](READMEru.md)

The free, open source PipelineCsv library is designed to work with the results of analysis of in-line flaw detection data in the form of a CSV file.

The library provides a set of high-level operations with CSV file.

Data can be

- mirrored
- glued together from several CSV files
- stretched/compressed along the distance according to a given set of intermediate points
- interpreted as an iterable sequence of pipes with geodata

## Installation

```bash
pip install pipeline-csv
```

## Usage

It is necessary to define the sets of defects and markers used in your project.
To do this, you need to define your class for CSV row by deriving it from the `pipeline_csv.csvfile.row.Row` class and
override two methods of this class: `defekts_dict` and `lineobj_dict`.

```python
from pipeline_csv.csvfile.row import Row

class TypeMarker:
    VALVE = 0
    CASE_START = 1
    CASE_END = 2

class TypeDefekt:
    CORROZ = 0
    DENT = 1
    FACTORY = 2

class MyRow(Row):

    @staticmethod
    def defekts_dict():
        return {
          TypeDefekt.CORROZ: "Corrosion",
          TypeDefekt.DENT: "Dent",
          TypeDefekt.FACTORY: "Manufacturing defect",
        }

    @staticmethod
    def lineobj_dict():
        return {
          TypeMarker.VALVE: "Valve",
          TypeMarker.CASE_START: "Casing start",
          TypeMarker.CASE_END: "Casing end",
        }
```

For the data mirroring operation, you need to override the `markers_reverse` method, which returns a dictionary that specifies the rules for replacing when mirroring.

```python
class MyRow(Row):

    @staticmethod
    def markers_reverse():
        return {
          TypeMarker.CASE_START: TypeMarker.CASE_END,
          TypeMarker.CASE_END: TypeMarker.CASE_START,
        }
```

Further, the MyRow class can be used in operations with data of CSV files.

- [Creating a CSV file](docs/en/csv_file.md)
- [Data mirroring](docs/en/mirror.md)
- [Docking new data and compression/stretching](docs/en/join.md)
- [Pipe sequence](docs/en/pipes.md)
- [Defect location at the pipe](docs/en/defekt_location.md)
- [Depth of defect](docs/en/defekt_depth.md)
- [Pipeline diameter changing](docs/en/diam.md)

## Development

```bash
git clone git@github.com:vb64/pipeline.csv.git
cd pipeline.csv
make setup PYTHON_BIN=/path/to/python3
make tests
```
