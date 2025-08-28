from typing import Dict, Any


class Patient:
    """Client for interacting with Patient in Eka Ecosystem"""
    def __init__(self, client):
        self.client = client

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Fetch the details of a specific patient.

        Args:
            patient_id (str): The ID of the patient to fetch

        Returns:
            dict: Patient details

        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> patient = client.patient.get_patient("YOUR_PATIENT_ID")
            >>> print(patient)
        """
        return self.client.request(
            method="GET",
            endpoint=f"/dr/v1/patient/{patient_id}"
        )