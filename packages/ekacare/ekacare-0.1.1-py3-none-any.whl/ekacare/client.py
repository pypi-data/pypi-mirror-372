import requests
from urllib.parse import urljoin
from typing import Dict, Any, Optional, Union

from .appointments.appointments import Appointments
from .doctor_clinic.clinic_doctor import ClinicAndDoctor
from .patient.patient import Patient
from .utils.exceptions import EkaCareAPIError, EkaCareAuthError
from .auth.auth import Auth
from .records.records import Records
from .tools.files import EkaFileUploader
from .vitals.vitals import Vitals
from .abdm.profile import Profile
from .webhooks.appointment import AppointmentWebhook
from .v2rx.v2rx import V2RX


class EkaCareClient:
    """
    Main client for interacting with the Eka Care API.
    
    Args:
        client_id (str): Your Eka Care API client ID
        client_secret (str): Your Eka Care API client secret
        base_url (str, optional): Base URL for the Eka Care API. Defaults to the production API URL.
    """
    
    def __init__(
        self, 
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.eka.care",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.session = requests.Session()
        self._access_token = access_token
        self.api_key = api_key
        
        # Initialize API modules
        self.auth = Auth(self)
        self.records = Records(self)
        self.files = EkaFileUploader(self)
        self.vitals = Vitals(self)
        self.abdm_profile = Profile(self)
        self.appointments = Appointments(self)
        self.patient  = Patient(self)
        self.clinic_doctor = ClinicAndDoctor(self)
        self.appointment_webhook = AppointmentWebhook(self)
        self.v2rx = V2RX(self)
        
    @property
    def access_token(self) -> str:
        """Get the current access token or request a new one if needed."""
        if not self._access_token:
            token_response = self.auth.login()
            self._access_token = token_response["access_token"]
        return self._access_token
    
    def set_access_token(self, token: str) -> None:
        """Manually set the access token."""
        self._access_token = token
    
    def request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], bytes, requests.Response]:
        """
        Make a request to the Eka Care API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Form data
            json (dict, optional): JSON body
            headers (dict, optional): Additional headers
            files (dict, optional): Files to upload
            auth_required (bool, optional): Whether auth token is required. Defaults to True.
            raw_response (bool, optional): Return the raw response object. Defaults to False.
            
        Returns:
            Union[dict, bytes, Response]: Response data, binary content, or response object
            
        Raises:
            EkaCareAPIError: If the API returns an error
            EkaCareAuthError: If authentication fails
        """
        url = urljoin(self.base_url, endpoint)
        
        if headers is None:
            headers = {}
            
        if auth_required:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        if self.client_id:
            headers["client-id"] = self.client_id
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            files=files
        )
        
        if raw_response:
            return response
            
        if not response.ok:
            if response.status_code == 401:
                raise EkaCareAuthError(
                    f"Authentication error: {response.status_code} - {response.text}"
                )
            raise EkaCareAPIError(
                f"API error {response.status_code}: {response.text}"
            )
            
        # Handle different response content types
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            return response.json()
        elif 'image/' in content_type or 'application/pdf' in content_type:
            return response.content
        elif not response.content:
            return {'status': 'success', 'status_code': response.status_code}
        else:
            try:
                return response.json()
            except ValueError:
                return response.text
