from typing import Dict, Any


class Appointments:
    """Client for interacting with Eka Appointment System"""

    def __init__(self, client):
        self.client = client

    def get_appointment_details(self, appointment_id: str) -> Dict[str, Any]:
        """
        Fetch the details of a specific appointment.

        Args:
            appointment_id (str): The ID of the appointment to fetch

        Returns:
            dict: Appointment details

        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> appointment = client.appointments.get_appointment_details("YOUR_APPOINTMENT_ID")
            >>> print(appointment)
        """
        return self.client.request(
            method="GET",
            endpoint=f"/dr/v1/appointment/{appointment_id}"
        )
