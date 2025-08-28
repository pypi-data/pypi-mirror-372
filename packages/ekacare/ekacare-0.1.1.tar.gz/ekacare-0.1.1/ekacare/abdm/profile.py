from typing import Dict, Any, Optional


class Profile:
    """Client for interacting with ABDM Profile APIs."""
    
    def __init__(self, client):
        self.client = client
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Fetch the ABHA profile of the user.
        
        Returns:
            dict: ABHA profile details
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> profile = client.abdm_profile.get_profile()
            >>> print(profile["abha_address"])
        """
        return self.client.request(
            method="GET",
            endpoint="/abdm/v1/profile"
        )
    
    def update_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the ABHA profile.
        
        Args:
            profile_data (dict): Profile data to update
            
        Returns:
            dict: Response indicating success
            
        Note:
            Fields like first_name, gender, date_of_birth cannot be modified for
            Aadhaar-based KYC verified profiles.
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> profile_data = {
            ...     "address": "123 Main St",
            ...     "pincode": "110001"
            ... }
            >>> client.abdm_profile.update_profile(profile_data)
        """
        return self.client.request(
            method="PATCH",
            endpoint="/abdm/v1/profile",
            json=profile_data
        )
    
    def delete_profile(self) -> Dict[str, Any]:
        """
        Delete the ABHA profile.
        
        Returns:
            dict: Response indicating success
            
        Warning:
            This permanently removes the ABHA profile with all associated documents and records.
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> client.abdm_profile.delete_profile()
        """
        return self.client.request(
            method="DELETE",
            endpoint="/abdm/v1/profile"
        )
    
    def get_abha_card(self) -> bytes:
        """
        Get the ABHA card as an image.
        
        Returns:
            bytes: PNG image data of the ABHA card
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> card_image = client.abdm_profile.get_abha_card()
            >>> with open("abha_card.png", "wb") as f:
            ...     f.write(card_image)
        """
        return self.client.request(
            method="GET",
            endpoint="/abdm/v1/profile/asset/card",
            raw_response=True
        ).content
    
    def get_abha_qr_code(self, format: str = "json") -> Dict[str, Any]:
        """
        Get the data for ABHA QR code display.
        
        Args:
            format (str): Response format (currently only "json" is supported)
            
        Returns:
            dict: QR code data
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> qr_data = client.abdm_profile.get_abha_qr_code()
            >>> # Use qr_data to generate a QR code image
        """
        return self.client.request(
            method="GET",
            endpoint="/abdm/v1/profile/asset/qr",
            params={"format": format}
        )
    
    def initiate_kyc(self, method: str, identifier: str) -> Dict[str, Any]:
        """
        Initiate the KYC process.
        
        Args:
            method (str): KYC method ("abha-number" or "aadhaar")
            identifier (str): ABHA number or Aadhaar number
            
        Returns:
            dict: Response containing transaction ID
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> response = client.abdm_profile.initiate_kyc(
            ...     method="abha-number",
            ...     identifier="1234-5678-9012"
            ... )
            >>> txn_id = response["txn_id"]
        """
        return self.client.request(
            method="POST",
            endpoint="/abdm/v1/profile/kyc/init",
            json={
                "method": method,
                "identifier": identifier
            }
        )
    
    def verify_kyc_otp(self, txn_id: str, otp: str) -> Dict[str, Any]:
        """
        Verify OTP for KYC.
        
        Args:
            txn_id (str): Transaction ID from initiate_kyc
            otp (str): OTP received
            
        Returns:
            dict: Response indicating success
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> client.abdm_profile.verify_kyc_otp(
            ...     txn_id="transaction123",
            ...     otp="123456"
            ... )
        """
        return self.client.request(
            method="POST",
            endpoint="/abdm/v1/profile/kyc/verify",
            json={
                "txn_id": txn_id,
                "otp": otp
            }
        )
    
    def resend_kyc_otp(self, txn_id: str) -> Dict[str, Any]:
        """
        Resend OTP for KYC.
        
        Args:
            txn_id (str): Transaction ID from initiate_kyc
            
        Returns:
            dict: Response containing the new transaction ID
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret", access_token="user_token")
            >>> response = client.abdm_profile.resend_kyc_otp("transaction123")
            >>> new_txn_id = response["txn_id"]
        """
        return self.client.request(
            method="POST",
            endpoint="/abdm/v1/profile/kyc/resend",
            json={"txn_id": txn_id}
        )
