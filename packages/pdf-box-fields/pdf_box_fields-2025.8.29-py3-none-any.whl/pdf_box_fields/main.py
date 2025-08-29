import argparse
import fitz
import logging
import os
from collections import defaultdict
from .config import (
    DEFAULT_INPUT_PDF,
    DEFAULT_CAPTURE_SUFFIX,
    DEFAULT_FIELD_GENERATOR_SUFFIX,
    DEFAULT_FILLER_SUFFIX,
    DEFAULT_MARKUP_SUFFIX,
    DEFAULT_FIELDS_SUFFIX,
    DEFAULT_FILL_SUFFIX,
)
from .extract import (
    extract_boxes,
    filter_boxes,
    remove_duplicates,
    sort_boxes,
)
from .layout import (
    calculate_layout_fields,
    assign_numeric_blocks,
)
from .io_utils import (
    write_csv,
    read_csv_rows,
    save_pdf_form_data_to_csv,
)
from .markup_and_fields import (
    markup_pdf,
    generate_form_fields_script,
    run_standalone_script,
    run_fill_pdf_fields,
)
from .utils import add_suffix_to_filename

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_log_handler = logging.StreamHandler()
_log_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
_log_handler.setFormatter(_log_formatter)
logger.addHandler(_log_handler)

def load_boxes_from_csv(csv_path):
    """
    Load boxes from a CSV file into a dictionary keyed by page number.

    Args:
        csv_path (str): Path to input CSV file.

    Returns:
        dict: Dictionary with page numbers as keys and lists of box dicts as values.
    """
    logger.info(f"Reading blocks from CSV: {csv_path}")
    rows = read_csv_rows(csv_path)
    page_dict = defaultdict(list)
    for row in rows:
        if row.get("page_num"):
            page_dict[int(row["page_num"])].append(row)
    return page_dict

def process_boxes(pdf_path, csv_path):
    """
    Extract white boxes from a PDF, filter them, remove duplicates, sort,
    calculate layout fields, and write CSV.

    Args:
        pdf_path (str): Path to input PDF file.
        csv_path (str): Output CSV file path for structured layout data.

    Returns:
        dict: Dictionary keyed by page with processed block data.
    """
    logger.info(f"Extracting boxes from PDF: {pdf_path}")
    boxes = extract_boxes(pdf_path)
    logger.info(f"Extracted {len(boxes)} white boxes.")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Error opening input PDF: {e}")
        return defaultdict(list)
    if logger.isEnabledFor(logging.DEBUG):
        write_csv(boxes, add_suffix_to_filename(csv_path, "-extracted"))
    filtered_boxes = []
    for page_num in range(1, len(doc) + 1):
        page_boxes = [p for p in boxes if p["page_num"] == page_num]
        filtered_boxes.extend(filter_boxes(doc[page_num - 1], page_boxes))
    doc.close()
    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, add_suffix_to_filename(csv_path, "-grouped"))
    filtered_boxes = remove_duplicates(filtered_boxes)
    filtered_boxes = sort_boxes(filtered_boxes, -1)
    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, add_suffix_to_filename(csv_path, "-filtered"))
    page_dict = calculate_layout_fields(filtered_boxes)
    if logger.isEnabledFor(logging.DEBUG):
        write_csv(filtered_boxes, add_suffix_to_filename(csv_path, "-layout"))
    page_dict = assign_numeric_blocks(page_dict)
    write_csv(page_dict, csv_path)
    return page_dict

def parse_arguments():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="PDF form fields generator with CSV and form script option."
    )
    parser.add_argument("--input-pdf", type=str, default=DEFAULT_INPUT_PDF, help="Input PDF filename")
    parser.add_argument("--input-csv", type=str, default=None, help="Input CSV file to reload blocks instead of generating")
    parser.add_argument("--markup", action="store_true", help="Mark up blocks in the output PDF")
    parser.add_argument("--fields", action="store_true", help="Generate and run standalone script to add form fields")
    parser.add_argument("--fill", action="store_true", help="Generate and run standalone script to fill form fields")
    parser.add_argument("--capture", action="store_true", help="Capture data from pdf form field to csv file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    """
    Main processing flow: dynamically track and update the input PDF filename
    through markup, fields, and fill steps depending on command-line options.
    """
    args = parse_arguments()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    current_input_pdf = args.input_pdf
    output_csv = os.path.splitext(current_input_pdf)[0] + ".csv"
    generator_script = os.path.splitext(current_input_pdf)[0] + DEFAULT_FIELD_GENERATOR_SUFFIX

    # Check for fatal error: --fill requires --input-csv
    if args.fill and not args.input_csv:
        logger.fatal("--fill requires --input-csv option.")
        exit(1)

    if args.input_csv:
        page_dict = load_boxes_from_csv(args.input_csv)
    else:
        page_dict = process_boxes(current_input_pdf, output_csv)

    if args.capture:
        capture_pdf = os.path.splitext(current_input_pdf)[0] + DEFAULT_CAPTURE_SUFFIX
        save_pdf_form_data_to_csv(current_input_pdf, capture_pdf)

    if args.markup:
        marked_up_pdf = add_suffix_to_filename(current_input_pdf, DEFAULT_MARKUP_SUFFIX)
        markup_pdf(current_input_pdf, page_dict, marked_up_pdf)
        current_input_pdf = marked_up_pdf

    if args.fields:
        fields_pdf = add_suffix_to_filename(current_input_pdf, DEFAULT_FIELDS_SUFFIX)
        script_path = generate_form_fields_script(args.input_csv or output_csv, current_input_pdf, fields_pdf, generator_script)
        run_standalone_script(script_path)
        current_input_pdf = fields_pdf

    if args.fill:
        filled_pdf = add_suffix_to_filename(current_input_pdf, DEFAULT_FILL_SUFFIX)
        filler_script = os.path.splitext(current_input_pdf)[0] + DEFAULT_FILLER_SUFFIX
        print(f"Filling PDF fields with CSV: {args.input_csv or output_csv}")
        run_fill_pdf_fields(args.input_csv or output_csv, filled_pdf, current_input_pdf, filler_script)
        print("Completed run_fill_pdf_fields()")

if __name__ == "__main__":
    main()
