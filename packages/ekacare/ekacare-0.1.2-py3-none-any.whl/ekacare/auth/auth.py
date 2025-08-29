from typing import Dict, Any


class Auth:
    """Authentication handler for Eka Care API."""
    
    def __init__(self, client):
        self.client = client
        
    def login(self) -> Dict[str, Any]:
        """
        Get an access token using client credentials.
        
        Returns:
            dict: Token response containing access_token, refresh_token, etc.
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> token_response = client.auth.login()
            >>> print(token_response["access_token"])
        """
        login_json = {
                "client_id": self.client.client_id,
                "client_secret": self.client.client_secret
            }
        if self.client.api_key is not None:
            login_json["api_key"] = self.client.api_key

        response = self.client.request(
            method="POST",
            endpoint="/connect-auth/v1/account/login",
            json=login_json,
            auth_required=False
        )
        return response
        
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token (str): The refresh token
            
        Returns:
            dict: Token response containing new access_token, refresh_token, etc.
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> new_tokens = client.auth.refresh_token("your_refresh_token")
            >>> client.set_access_token(new_tokens["access_token"])
        """
        response = self.client.request(
            method="POST",
            endpoint="/connect-auth/v1/account/refresh",
            json={
                "refresh_token": refresh_token
            },
            auth_required=False
        )
        return response
