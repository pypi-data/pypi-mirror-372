from typing import Dict, Any, List


class Vitals:
    """Client for interacting with Eka Care Vitals API."""
    
    def __init__(self, client):
        self.client = client
        
    def update_vitals(self, txn_id: str, vitals_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update patient vitals.
        
        Args:
            txn_id (str): Transaction ID for the vitals update
            vitals_data (list): List of vital records to update
            
        Returns:
            dict: Response indicating success or failure
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> heart_rate = client.vitals.create_heart_rate_vital(75, "2023-01-01T12:00:00")
            >>> blood_glucose = client.vitals.create_blood_glucose_vital(120, "2023-01-01T08:00:00", "fasting")
            >>> response = client.vitals.update_vitals("txn123", [heart_rate, blood_glucose])
        """
        return self.client.request(
            method="PUT",
            endpoint=f"/api/v1/vitals/{txn_id}",
            json={"vitals": vitals_data}
        )
        
    def create_heart_rate_vital(
        self,
        value: float,
        measured_at: str,
        unit: str = "{Counts}/min"
    ) -> Dict[str, Any]:
        """
        Create a heart rate vital record.
        
        Args:
            value (float): Heart rate value
            measured_at (str): Timestamp of measurement (ISO format)
            unit (str, optional): Unit of measurement
            
        Returns:
            dict: Vital record ready for submission
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> heart_rate = client.vitals.create_heart_rate_vital(75, "2023-01-01T12:00:00")
        """
        return {
            "vital_display_name": "heart_rate",
            "vital_loinc_code": "8867-4",
            "vital_value": {
                "vital_numeric_value": value,
                "vital_boolean_value": None,
                "vital_string_value": None
            },
            "unit_display_name": unit,
            "unit_ucum_code": "<ucum code>",
            "measured_at": {
                "DateTime": measured_at,
                "instant": None,
                "period": {
                    "startDateTime": None,
                    "endDateTime": None
                }
            }
        }
        
    def create_blood_glucose_vital(
        self,
        value: float,
        measured_at: str,
        glucose_type: str = "random",
        unit: str = "mg/dL"
    ) -> Dict[str, Any]:
        """
        Create a blood glucose vital record.
        
        Args:
            value (float): Blood glucose value
            measured_at (str): Timestamp of measurement (ISO format)
            glucose_type (str, optional): Type of glucose measurement
                (random, fasting, after_food)
            unit (str, optional): Unit of measurement
            
        Returns:
            dict: Vital record ready for submission
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> glucose = client.vitals.create_blood_glucose_vital(120, "2023-01-01T08:00:00", "fasting")
        """
        vital_types = {
            "random": {
                "name": "random_blood_glucose",
                "loinc_code": "74774-1"
            },
            "fasting": {
                "name": "fasting_blood_glucose",
                "loinc_code": "1558-6"
            },
            "after_food": {
                "name": "after_food_blood_glucose",
                "loinc_code": "1521-4"
            }
        }
        
        vital_type = vital_types.get(glucose_type, vital_types["random"])
        
        return {
            "vital_display_name": vital_type["name"],
            "vital_loinc_code": vital_type["loinc_code"],
            "vital_value": {
                "vital_numeric_value": value,
                "vital_boolean_value": None,
                "vital_string_value": None
            },
            "unit_display_name": unit,
            "unit_ucum_code": unit,
            "measured_at": {
                "DateTime": measured_at,
                "instant": None,
                "period": {
                    "startDateTime": None,
                    "endDateTime": None
                }
            }
        }
        
    def create_blood_oxygen_vital(
        self,
        value: float,
        measured_at: str,
        unit: str = "%"
    ) -> Dict[str, Any]:
        """
        Create a blood oxygen (SpO2) vital record.
        
        Args:
            value (float): Blood oxygen saturation value
            measured_at (str): Timestamp of measurement (ISO format)
            unit (str, optional): Unit of measurement
            
        Returns:
            dict: Vital record ready for submission
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> oxygen = client.vitals.create_blood_oxygen_vital(98, "2023-01-01T12:30:00")
        """
        return {
            "vital_display_name": "blood_oxygen",
            "vital_loinc_code": "2708-6",
            "vital_value": {
                "vital_numeric_value": value,
                "vital_boolean_value": None,
                "vital_string_value": None
            },
            "unit_display_name": unit,
            "unit_ucum_code": unit,
            "measured_at": {
                "DateTime": measured_at,
                "instant": None,
                "period": {
                    "startDateTime": None,
                    "endDateTime": None
                }
            }
        }
        
    def create_blood_pressure_vital(
        self,
        systolic: float,
        diastolic: float,
        measured_at: str,
        unit: str = "mm Hg"
    ) -> List[Dict[str, Any]]:
        """
        Create blood pressure vital records (systolic and diastolic).
        
        Args:
            systolic (float): Systolic blood pressure value
            diastolic (float): Diastolic blood pressure value
            measured_at (str): Timestamp of measurement (ISO format)
            unit (str, optional): Unit of measurement
            
        Returns:
            list: List of vital records ready for submission
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> bp_vitals = client.vitals.create_blood_pressure_vital(120, 80, "2023-01-01T14:45:00")
        """
        systolic_vital = {
            "vital_display_name": "systolic_bp",
            "vital_loinc_code": "8480-6",
            "vital_value": {
                "vital_numeric_value": systolic,
                "vital_boolean_value": None,
                "vital_string_value": None
            },
            "unit_display_name": unit,
            "unit_ucum_code": unit,
            "measured_at": {
                "DateTime": measured_at,
                "instant": None,
                "period": {
                    "startDateTime": None,
                    "endDateTime": None
                }
            }
        }
        
        diastolic_vital = {
            "vital_display_name": "diastolic_bp",
            "vital_loinc_code": "8462-4",
            "vital_value": {
                "vital_numeric_value": diastolic,
                "vital_boolean_value": None,
                "vital_string_value": None
            },
            "unit_display_name": unit,
            "unit_ucum_code": unit,
            "measured_at": {
                "DateTime": measured_at,
                "instant": None,
                "period": {
                    "startDateTime": None,
                    "endDateTime": None
                }
            }
        }
        
        return [systolic_vital, diastolic_vital]
