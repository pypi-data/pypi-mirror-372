# pdf-box-fields

Tools for extracting, processing, and generating interactive fields for PDFs containing white box form elements.

***

## Overview

**pdf-box-fields** is a Python library and command-line tool designed to help developers automate the extraction, manipulation, and generation of interactive form fields within PDFs that use white box placeholders. Whether you need to analyze PDF layouts, mark up fields visually, generate interactive form widgets, or fill and capture form data from PDFs — this toolkit provides a robust, modular solution powered by PyMuPDF and PyPDFForm.

***

## Key Features

- **Box extraction:** Precisely extract white (filled) box regions from PDFs as potential form fields.
- **Layout processing:** Analyze and group extracted boxes by page, line, and block with flexible gap detection.
- **Form field generation:** Automatically produce Python scripts to create interactive PDF form fields aligned with detected boxes.
- **Markup visualization:** Generate annotated PDFs marked with box locations and identifiers for debugging and verification.
- **Form filling and capture:** Fill PDF form fields programmatically from CSV data and capture filled data back into CSV.
- **CLI integration:** A user-friendly command-line interface to chain extraction, markup, field generation, filling, and capturing workflows.
- **Extensible \& Open Source:** Easily customize or extend to your specific PDF data extraction and form automation needs.

***

## Installation

For clean installation isolated from other packages, use [pipx](https://pipxproject.github.io/pipx/):

```bash
pipx install pdf-box-fields
```

Or install with pip into your environment:

```bash
pip install pdf-box-fields
```


***

## Usage

Run the CLI tool with your PDF files:

```bash
pdf-box-fields --input-pdf myfile.pdf --markup
```

Common options:

- `--markup` → Mark up detected white boxes in the PDF for visual inspection.
- `--fields` → Generate and execute scripts to add interactive form fields to the PDF.
- `--fill` → Fill generated form fields programmatically with data from a CSV.
- `--capture` → Extract filled form field data back into a CSV file.
- `--input-csv` → Use a CSV file of box data instead of extracting boxes anew.
- `--verbose` → Enable verbose logging output for debugging.

Example workflow:

```bash
pdf-box-fields --input-pdf form_template.pdf --markup --fields
pdf-box-fields --input-pdf form_template-fields.pdf --input-csv form_template.csv --fill
pdf-box-fields --input-pdf form_template-filled.pdf --capture
```


***

## For Developers

Clone the repository and install development dependencies:

```bash
git clone https://github.com/yourusername/pdf-box-fields.git
cd pdf-box-fields
pip install -e .[dev]
```

Run tests with coverage:

```bash
tox
```

Test CLI help endpoint:

```bash
python -m pdf_box_fields.cli --help
```

The project is modular, with clearly separated components (`extract`, `layout`, `markup_and_fields`, `io_utils`, `utils`) for easy maintenance and extension.

***

## License

This project is licensed under the **GNU General Public License v3.0 or later** (GPL-3.0-or-later). See [LICENSE](LICENSE) for details.

***

## Contributing

Contributions are warmly welcomed! Please open issues for bugs or feature requests, and submit pull requests with tests and documentation improvements.

***

## Acknowledgements

- Uses [PyMuPDF](https://pymupdf.readthedocs.io) for PDF parsing and rendering.
- Uses [PyPDFForm](https://pypdfform.readthedocs.io) for PDF form creation and filling.
- Inspired by the need for reliable automation of PDF form workflows involving white box placeholders.

***