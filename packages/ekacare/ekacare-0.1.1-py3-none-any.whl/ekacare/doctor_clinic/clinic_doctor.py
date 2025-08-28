from typing import Dict, Any


class ClinicAndDoctor:
    """Client for getting clinic details"""

    def __init__(self, client):
        self.client = client

    def get_clinic_details(self, clinic_id: str) -> Dict[str, Any]:
        """
        Fetch the details of a specific appointment.

        Args:
            clinic_id (str): The ID of the appointment to fetch

        Returns:
            dict: Clinic details

        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> clinic = client.clinic_doctor.get_clinic_details("YOUR_CLINIC_ID")
            >>> print(clinic)
        """
        return self.client.request(
            method="GET",
            endpoint=f"/dr/v1/business/clinic/{clinic_id}"
        )


    def get_doctor_details(self, doctor_id: str) -> Dict[str, Any]:
        """
        Fetch the details of a specific appointment.

        Args:
            doctor_id (str): The ID of the appointment to fetch

        Returns:
            dict: Clinic details

        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> clinic = client.clinic_doctor.get_doctor_details("YOUR_DOCTOR_ID")
            >>> print(clinic)
        """
        return self.client.request(
            method="GET",
            endpoint=f"/dr/v1/doctor/{doctor_id}"
        )
