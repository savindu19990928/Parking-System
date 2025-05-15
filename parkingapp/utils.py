import os
import io
import json
from tempfile import NamedTemporaryFile
from pyreportjasper import PyReportJasper
from django.conf import settings

def generate_report_from_json(file_name: str, data: dict, parameters: dict = None) -> io.BytesIO:
    """
    Generate a Jasper report as PDF from JSON data instead of DB.

    :param file_name: Name of the .jasper file in the reports directory
    :param data: JSON-serializable dict to use as Jasper data source (should have a root node matching json_query)
    :param parameters: Optional report parameters
    :return: BytesIO containing PDF report
    """
    parameters = parameters or {}
    reports_dir = os.path.join(settings.BASE_DIR, 'reports')
    input_path = os.path.join(reports_dir, file_name)

    # Write JSON data to temp file
    with NamedTemporaryFile(suffix=".json", mode='w+', delete=False) as json_file:
        json.dump(data, json_file)
        json_file_path = json_file.name

    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_basename = os.path.splitext(tmp_file.name)[0]

    try:
        jasper = PyReportJasper()
        jasper.config(
            input_file=input_path,
            output_file=tmp_basename,
            output_formats=["pdf"],
            parameters=parameters,
            db_connection={
                'data_file': json_file_path,
                'data_type': 'json',
                'json_query': 'data'  # adjust if your root JSON node is different
            }
        )
        jasper.process_report()

        pdf_path = f"{tmp_basename}.pdf"
        with open(pdf_path, "rb") as pdf_file:
            return io.BytesIO(pdf_file.read())

    finally:
        os.remove(json_file_path)
        if os.path.exists(f"{tmp_basename}.pdf"):
            os.remove(f"{tmp_basename}.pdf")
