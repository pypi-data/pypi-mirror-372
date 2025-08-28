import os
from typing import Dict, Any, List, Optional

from ..utils.exceptions import EkaCareValidationError


class Records:
    """Client for interacting with Eka Care Records API."""
    
    def __init__(self, client):
        self.client = client
        
    def get_authorization(self, batch_request: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Obtain authorization for uploading documents.
        
        Args:
            batch_request (list): List of document requests
            
        Returns:
            dict: Response containing presigned URLs for upload
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> batch_request = [{
            ...     "dt": "lr",  # lab report
            ...     "dd_e": 1614556800,  # document date in epoch format
            ...     "tg": ["covid", "test"],  # tags
            ...     "files": [{
            ...         "contentType": "application/pdf",
            ...         "file_size": 1024000  # size in bytes
            ...     }]
            ... }]
            >>> auth_response = client.records.get_authorization(batch_request)
        """
        return self.client.request(
            method="POST",
            endpoint="/mr/api/v1/docs",
            json={"batch_request": batch_request}
        )
        
    def upload_document(
        self, 
        file_path: str, 
        document_type: str,
        document_date: Optional[int] = None,
        tags: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to Eka Care.
        
        Args:
            file_path (str): Path to the file to upload
            document_type (str): Type of document (e.g., 'lr' for lab report, 'ps' for prescription)
            document_date (int, optional): Document date as epoch timestamp
            tags (list, optional): List of tags for the document
            title (str, optional): Title for the document
            
        Returns:
            dict: Response containing document ID
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> response = client.records.upload_document(
            ...     file_path="/path/to/lab_report.pdf",
            ...     document_type="lr",
            ...     tags=["covid", "test"],
            ...     title="COVID-19 Test Report"
            ... )
            >>> document_id = response["document_id"]
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get file size and content type
        file_size = os.path.getsize(file_path)
        content_type = self._get_content_type(file_path)
        
        # Prepare batch request
        batch_request = [{
            "dt": document_type,
            "dd_e": document_date,
            "tg": tags or [],
            "files": [
                {
                    "contentType": content_type,
                    "file_size": file_size
                }
            ]
        }]
        
        if title:
            batch_request[0]["title"] = title
        
        # Get presigned URL for upload
        auth_response = self.get_authorization(batch_request)
        
        # Upload the file using the presigned URL
        batch_response = auth_response.get("batch_response", [])
        if not batch_response:
            raise EkaCareValidationError("No upload URL received")
            
        document_id = batch_response[0].get("document_id")
        forms = batch_response[0].get("forms", [])
        
        if not forms:
            raise EkaCareValidationError("No upload forms received")
            
        form = forms[0]
        upload_url = form.get("url")
        fields = form.get("fields", {})
        
        # Prepare the form data for the upload
        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file, content_type)}
            
            # Use requests session directly to upload to the presigned URL
            response = self.client.session.post(
                url=upload_url,
                data=fields,
                files=files
            )
            
        if not response.ok:
            raise EkaCareValidationError(f"Upload failed: {response.text}")
            
        return {"document_id": document_id}
        
    def list_documents(
        self,
        updated_after: Optional[int] = None,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List documents.
        
        Args:
            updated_after (int, optional): Filter documents updated after this timestamp
            next_token (str, optional): Token for pagination
            
        Returns:
            dict: Response containing list of documents
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> documents = client.records.list_documents()
            >>> for doc in documents["items"]:
            ...     print(doc["record"]["item"]["document_id"])
        """
        params = {}
        if updated_after:
            params["u_at__gt"] = updated_after
        if next_token:
            params["offset"] = next_token
            
        return self.client.request(
            method="GET",
            endpoint="/mr/api/v1/docs",
            params=params,
            headers={"accept": "application/json"}
        )
        
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get details of a specific document.
        
        Args:
            document_id (str): ID of the document
            
        Returns:
            dict: Document details
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> document = client.records.get_document("document123")
            >>> print(document["document_type"])
        """
        return self.client.request(
            method="GET",
            endpoint=f"/mr/api/v1/docs/{document_id}"
        )
        
    def update_document(
        self,
        document_id: str,
        document_type: Optional[str] = None,
        document_date: Optional[int] = None,
        tags: Optional[List[str]] = None,
        ndhm: Optional[bool] = None,
        oid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a document's metadata.
        
        Args:
            document_id (str): ID of the document
            document_type (str, optional): Type of document (e.g., 'lr' for lab report)
            document_date (int, optional): Document date as epoch timestamp
            tags (list, optional): List of tags for the document
            ndhm (bool, optional): Whether to link the document to NDHM
            oid (str, optional): OID to associate with the document
            
        Returns:
            dict: Empty response on success
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> client.records.update_document(
            ...     document_id="document123",
            ...     document_type="ps",
            ...     tags=["medication"]
            ... )
        """
        data = {}
        if document_type:
            data["dt"] = document_type
        if document_date:
            data["dd_e"] = document_date
        if tags:
            data["tg"] = tags
        if ndhm is not None:
            data["ndhm"] = ndhm
        if oid:
            data["oid"] = oid
            
        return self.client.request(
            method="PATCH",
            endpoint=f"/mr/api/v1/docs/{document_id}",
            json=data
        )
        
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document.
        
        Args:
            document_id (str): ID of the document
            
        Returns:
            dict: Empty response on success
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> client.records.delete_document("document123")
        """
        return self.client.request(
            method="DELETE",
            endpoint=f"/mr/api/v1/docs/{document_id}"
        )
    
    def retrieve_health_records(self, 
                               identifier: str, 
                               hip_id: Optional[str] = None, 
                               health_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve health records in FHIR format.
        
        Args:
            identifier (str): Care context ID
            hip_id (str, optional): Health Information Provider ID
            health_id (str, optional): ABHA address
            
        Returns:
            dict: FHIR bundle containing health records
            
        Example:
            >>> client = EkaCareClient(client_id="your_id", client_secret="your_secret")
            >>> records = client.records.retrieve_health_records(
            ...     identifier="care_context_123",
            ...     hip_id="hip123",
            ...     health_id="user@abdm"
            ... )
        """
        params = {"identifier": identifier}
        if hip_id:
            params["hip_id"] = hip_id
        if health_id:
            params["health_id"] = health_id
            
        return self.client.request(
            method="GET",
            endpoint="/health/api/v1/fhir/retrieve",
            params=params
        )
        
    def _get_content_type(self, file_path: str) -> str:
        """Determine content type based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf"
        }
        return content_types.get(ext, "application/octet-stream")
