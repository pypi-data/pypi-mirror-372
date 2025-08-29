from typing import Dict, Any, Optional, Set
from ekacare.webhooks.enums import FetchType


class AppointmentWebhook:
    """Client for interacting with Eka Appointment Webhooks"""

    def __init__(self, client):
        self.client = client

    def get_detailed_appointment_data(
        self,
        payload: Dict[str, Any],
        fetch: Set[FetchType]  # MANDATORY
    ) -> Dict[str, Any]:
        """
        Fetch specified data only (caller must pass what they need explicitly).

        Args:
            payload (dict): Webhook payload
            fetch (Set[FetchType]): Set of data types to fetch

        Returns:
            dict: Aggregated result
        """
        data = payload.get("data", {})
        appointment_id = data.get("appointment_id")
        patient_id = data.get("patient_id")
        clinic_id = data.get("clinic_id")
        doctor_id = data.get("doctor_id")

        if FetchType.APPOINTMENT in fetch and not appointment_id:
            raise ValueError("Missing appointment_id in payload")
        if FetchType.PATIENT in fetch and not patient_id:
            raise ValueError("Missing patient_id in payload")
        if FetchType.CLINIC in fetch and not clinic_id:
            raise ValueError("Missing clinic_id in payload")
        if FetchType.DOCTOR in fetch and not doctor_id:
            raise ValueError("Missing doctor_id in payload")

        result = {}

        if FetchType.APPOINTMENT in fetch:
            appointment_details = self.client.appointments.get_appointment_details(appointment_id)
            appointment_details["rescheduled"] = False

            old_aid = data.get("p_aid")
            if old_aid and isinstance(old_aid, str):
                appointment_details["rescheduled"] = True
                appointment_details["old_appointment_details"] = self.client.appointments.get_appointment_details(old_aid)

            result["appointment_details"] = appointment_details

        if FetchType.PATIENT in fetch:
            result["patient_details"] = self.client.patient.get_patient(patient_id)

        if FetchType.CLINIC in fetch:
            result["clinic_details"] = self.client.clinic_doctor.get_clinic_details(clinic_id)

        if FetchType.DOCTOR in fetch:
            result["doctor_details"] = self.client.clinic_doctor.get_doctor_details(doctor_id)

        return result