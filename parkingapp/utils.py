import requests
import io
import json
import os

def generate_remote_report(
    endpoint_url: str,
    jasper_file_path: str,
    data: list,
    parameters: dict = None,
    timeout: int = 60
) -> io.BytesIO:
    """
    Sends a .jasper file, JSON data (as a file), and parameters to the Jasper report API and returns the generated PDF.
    """

    # JSON object (structured correctly)
    json_payload = json.dumps({ "ABC": data }, indent=2)

    # Create a file-like object from JSON string
    json_file = io.BytesIO(json_payload.encode('utf-8'))
    json_file.name = "data.json"

    with open(jasper_file_path, 'rb') as jasper_file:
        files = {
            'jasperFile': (os.path.basename(jasper_file_path), jasper_file, 'application/octet-stream'),
            'jsonData': ("data.json", json_file, 'application/json')
        }

        # Optional parameters as form-data
        data_fields = parameters or {}

        response = requests.post(endpoint_url, files=files, data=data_fields, timeout=timeout)
        print("RESPONSE TEXT:", response.text)
        response.raise_for_status()

        if 'application/pdf' not in response.headers.get('Content-Type', ''):
            raise ValueError("Expected PDF response, got: " + response.headers.get('Content-Type', ''))

        return io.BytesIO(response.content)
