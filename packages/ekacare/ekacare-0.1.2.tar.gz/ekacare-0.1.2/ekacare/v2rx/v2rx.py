from typing import Dict, Any
from io import BytesIO
import requests
import json
import os
from urllib.parse import urlencode, urlparse

class EkaScribeError(Exception):
    """Upload related errors for EkaScribe"""
    pass

class V2RX:
    """
    Client for interacting with V2RX (Ekascribe) session status APIs.
    This is typically used to fetch the results of an audio transcription job
    initiated via the file upload mechanism with action 'ekascribe'.
    """

    def __init__(self, client):
        """
        Initialize the V2RX client.

        Args:
            client: The EkaCareClient instance.
        """
        self.client = client

    def get_s3_bucket_name(self, url):
        parsed = urlparse(url)
        # Example: 'm-prod-ekascribe-batch.s3.amazonaws.com' → 'm-prod-ekascribe-batch'
        domain_parts = parsed.netloc.split('.')
        if 's3' in domain_parts:
            return domain_parts[0]
        return None


    def upload(self, file_paths, txn_id=None, action='default', extra_data={}, output_format={}):
        print("Uploading files to Ekascribe...")
        file_upload_result = self.client.files.upload(
            file_paths=file_paths,
            txn_id=txn_id,
            action=action,
            extra_data=extra_data,
            output_format=output_format
        )
        upload_info = self.client.files.get_last_upload_info()

        print("Uploading files to Ekascribe success...")
        if action == 'ekascribe-v2':
            try:
                bucket_name = self.get_s3_bucket_name(upload_info['uploadData']['url'])
                folder_path = upload_info['folderPath']
                
                s3_url = f"s3://{bucket_name}/{folder_path}"

                s3_file_paths = []

                for file in file_paths:
                    file_name = os.path.basename(file)
                    s3_file_paths.append(f"{s3_url}{file_name}")
                
                payload = {
                        "s3_url": s3_url,
                        "batch_s3_url": s3_url,
                        "additional_data": extra_data,
                        "mode": extra_data.get('mode'),
                        "input_language": output_format.get('input_language'),
                        "speciality": "speciality",
                        "Section": "section",
                        "output_format_template": output_format.get('output_template'),
                        "transfer": "non-vaded",
                        "client_generated_files": s3_file_paths,
                        "model_type": extra_data.get('model_type', 'pro'),
                    }
                auth_headers = {
                        "Authorization": f"Bearer {self.client.access_token}",
                    }
                resp = requests.post(
                    url=f"https://api.eka.care/voice/api/v2/transaction/init/{txn_id}",
                    headers=auth_headers,
                    json=payload
                )
                if resp.status_code != 201:
                    raise EkaScribeError(f"Upload initialisation failed: {resp.json()}")

            except Exception as e:
                raise EkaScribeError(f"Upload failed: {str(e)}")
        
        return file_upload_result

    def get_session_status(self, session_id: str, action="ekascribe") -> Dict[str, Any]:
        """
        Fetch the status and results of a voice recording session (Ekascribe job).

        After uploading an audio file for Ekascribe and receiving a webhook notification
        indicating completion, this method can be used to retrieve the transcription results.
        The `session_id` is typically part of the webhook payload.

        Args:
            session_id (str): The ID of the voice recording session.

        Returns:
            dict: A dictionary containing the session status information.
                  This includes the status of the job (e.g., "completed", "failed")
                  and, if successful, the output data, which often contains a
                  base64 encoded FHIR bundle.

        Raises:
            ValueError: If the session_id is null or empty.
            EkaCareAPIError: If the API call fails or returns an error status.

        Example:
            >>> # client is an instance of EkaCareClient
            >>> # session_id is obtained from the webhook after audio processing
            >>> status_response = client.v2rx.get_session_status("your_session_id_here")
            >>> print(f"Job Status: {status_response.get('status')}")
            >>> if status_response.get('status') == 'completed':
            ...     fhir_base64 = status_response.get('data', {}).get('output', {}).get('fhir')
            ...     if fhir_base64:
            ...         # Decode and process the FHIR data
            ...         pass
        """
        if not session_id:
            raise ValueError("Session ID cannot be null or empty")
        
        endpoint = f"/voice-record/api/status/{session_id}"
        
        if action == "ekascribe-v2":
            endpoint = f"voice/api/v3/status/{session_id}"

        return self.client.request(method="GET", endpoint=endpoint)