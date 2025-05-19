import requests
import io
import json
import os

def generate_remote_report(
    endpoint_url: str,
    jasper_file_path: str,
    data: list,
    parameters: dict = None,
    logo_file_path: str = None,
    timeout: int = 60
) -> io.BytesIO:
    """
    Sends a .jasper file, JSON data, optional logo file, and parameters to the Jasper report API.
    Returns the generated PDF as BytesIO.
    """
    # Prepare JSON data for the data source
    json_payload = json.dumps({"ABC": data}, indent=2)
    json_file = io.BytesIO(json_payload.encode('utf-8'))
    json_file.name = "data.json"

    # Open the jasper file and optionally the logo file
    with open(jasper_file_path, 'rb') as jasper_file:
        files = {
            'jasperFile': (os.path.basename(jasper_file_path), jasper_file, 'application/octet-stream'),
            'jsonData': ("data.json", json_file, 'application/json')
        }

        # 👇 Include logo if provided
        if logo_file_path:
            with open(logo_file_path, 'rb') as logo_file:
                files['logo'] = (os.path.basename(logo_file_path), logo_file, 'image/jpg')

                # Send request with logo
                response = requests.post(endpoint_url, files=files, data=parameters or {}, timeout=timeout)
        else:
            # Send request without logo
            response = requests.post(endpoint_url, files=files, data=parameters or {}, timeout=timeout)

    response.raise_for_status()

    if 'application/pdf' not in response.headers.get('Content-Type', ''):
        raise ValueError("Expected PDF response, got: " + response.headers.get('Content-Type', ''))

    return io.BytesIO(response.content)
