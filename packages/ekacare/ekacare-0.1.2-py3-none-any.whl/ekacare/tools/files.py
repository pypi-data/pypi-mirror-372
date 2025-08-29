import requests
import os
import mimetypes
import boto3
from urllib.parse import urlencode, urlparse
import uuid
from io import BytesIO
import json


class EkaUploadError(Exception):
    """Upload related errors for Eka File Uploader"""
    pass

class EkaFileUploader:
    """
    Eka File Uploader SDK
    A simple and efficient way to handle authenticated file uploads to S3
    """
    def __init__(self, client):
        self.client = client
        self.__upload_info = None

    def get_s3_bucket_name(self, url):
        parsed = urlparse(url)
        # Example: 'm-prod-ekascribe-batch.s3.amazonaws.com' → 'm-prod-ekascribe-batch'
        domain_parts = parsed.netloc.split('.')
        if 's3' in domain_parts:
            return domain_parts[0]
        return None
    
    def get_upload_location(self, txn_id=None, action='ekascribe', extra_data={}):
        """
        Get S3 upload location
        
        Args:
            txn_id (str, optional): Transaction ID for grouping uploads
            
        Returns:
            dict: Upload location information
        """
        try:
            params = {}
            if txn_id:
                params['txn_id'] = txn_id
                params['action'] =  action
        
            response = self.client.request(
                method="POST",
                endpoint=f"/v1/file-upload?{urlencode(params)}",
                json=extra_data
            )
            return response
        except Exception as e:
            raise EkaUploadError(f"Error getting upload location: {str(e)}")
        
    def push_ekascribe_json(self, audio_files, txn_id, extra_data={}, upload_info={}, output_format = {}):
        s3_post_data = upload_info['uploadData']
        folder_path = upload_info['folderPath']
        s3_post_data['fields']['key'] = folder_path + txn_id + '.json'
        data = {
            "client-id": self.client.client_id,
            "transaction-id": txn_id,
            "audio-file": [],
            "transfer": "non-vaded"
        }
        for item in audio_files:
            data['audio-file'].append(item.split('/')[-1])
        data["additional_data"] = extra_data
        data["output_format"] = output_format
        data.update(extra_data)
        json_bytes = BytesIO(json.dumps(data, indent=2).encode('utf-8'))
        files = {'file': ('data.json', json_bytes.getvalue(), 'application/json')}

        response = requests.post(
            s3_post_data['url'],
            data=s3_post_data['fields'],
            files=files
        )
        if response.status_code != 204:
            raise EkaUploadError(f"Upload failed: {response.text}")
        return {
            'key': folder_path + txn_id + '.json',
            'contentType': 'application/json',
            'size': len(json_bytes.getvalue())
        }

    def upload(self, file_paths, txn_id=None, action='default',extra_data={}, output_format={}):
        """
        Upload a file to S3
        
        Args:
            file_path (str): Path to the file to upload
            txn_id (str, optional): Transaction ID for grouping uploads
            action (str, optional): Action to perform on the file, one of ['ekascribe', 'default']
            extra_data (dict, optional): Extra data to send with the upload request
            
        Returns:
            dict: Upload result containing key, content type, and size
        """
        try:
            return_list = []
            if not txn_id:
                txn_id = str(uuid.uuid4())
            upload_info = self.get_upload_location(txn_id, action=action, extra_data=extra_data)
            self.__upload_info = upload_info

            for file_path in file_paths: 
                file_size = os.path.getsize(file_path)
                if file_size > 100 * 1024 * 1024:  # 100MB threshold
                    return_list.append(self._upload_large_file(
                        upload_info['uploadData'],
                        upload_info['folderPath'],
                        file_path
                    ))
                else:
                    return_list.append(self._upload_single_file(
                        upload_info['uploadData'],
                        upload_info['folderPath'],
                        file_path
                    ))
            
            
            if action == 'ekascribe' or action =='ekascribe-v2':
                self.push_ekascribe_json(file_paths, txn_id, extra_data = extra_data, upload_info= upload_info, output_format=output_format)


            return return_list
        except Exception as e:
            raise EkaUploadError(f"Upload failed: {str(e)}")
        
    def _upload_single_file(self, upload_data, folder_path, file_path):
        """Internal method to handle single file upload"""
        file_name = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        s3_post_data = upload_data
        s3_post_data['fields']['key'] = folder_path + file_name
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_name, file, content_type)
                }
                
                # Optimized request configuration
                response = requests.post(
                    s3_post_data['url'],
                    data=s3_post_data['fields'],
                    files=files,
                    timeout=(30, 1800),  # 30s connect, 30min read timeout
                    stream=False,  # Let requests handle memory efficiently
                )
                
                if response.status_code != 204:
                    raise EkaUploadError(f"Upload failed for {file_name}: HTTP {response.status_code} - {response.text}")
                
                print(f"Successfully uploaded {file_name}")
                
                return {
                    'key': folder_path + file_name,
                    'contentType': content_type,
                    'size': os.path.getsize(file_path)
                }
                
        except requests.exceptions.Timeout:
            raise EkaUploadError(f"Upload timeout for {file_name}. File may be too large or connection too slow.")
        except requests.exceptions.ConnectionError:
            raise EkaUploadError(f"Connection error while uploading {file_name}. Check network connectivity.")
        except Exception as e:
            raise EkaUploadError(f"Unexpected error uploading {file_name}: {str(e)}")

    def _upload_large_file(self, upload_data, folder_path, file_path):
        """Internal method to handle large file upload using multipart"""
        file_name = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        file_size = os.path.getsize(file_path)
        
        s3_post_data = upload_data
        s3_post_data['fields']['key'] = folder_path + file_name
        
        try:
            # Use a custom file wrapper for progress tracking
            with ChunkedFileReader(file_path, chunk_size=8192) as chunked_file:
                files = {
                    'file': (file_name, chunked_file, content_type)
                }
                
                response = requests.post(
                    s3_post_data['url'],
                    data=s3_post_data['fields'],
                    files=files,
                    timeout=(30, 1800)
                )
                
                if response.status_code != 204:
                    raise EkaUploadError(f"Upload failed for {file_name}: HTTP {response.status_code} - {response.text}")
                
                print(f"Successfully uploaded {file_name}")
                
                return {
                    'key': folder_path + file_name,
                    'contentType': content_type,
                    'size': file_size
                }
                
        except Exception as e:
            raise EkaUploadError(f"Memory-efficient upload failed for {file_name}: {str(e)}")


    def get_last_upload_info(self):
        """
        Get the upload info from the most recent upload operation.
        
        Returns:
            dict: Upload info from the last successful upload, or None if no upload has been performed
        """
        if self.__upload_info is None:
            return None
        return self.__upload_info.copy()
    

class ChunkedFileReader:
    """
    File-like object that reads in chunks for memory efficiency
    """
    def __init__(self, file_path, chunk_size=8192):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.file = None
        self.total_size = os.path.getsize(file_path)
        self.bytes_read = 0
        
    def __enter__(self):
        self.file = open(self.file_path, 'rb')
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
    
    def read(self, size=-1):
        if not self.file:
            return b''
        
        if size == -1:
            size = self.chunk_size
        
        chunk = self.file.read(min(size, self.chunk_size))
        self.bytes_read += len(chunk)
        
        # Progress reporting (optional)
        if self.bytes_read % (1024 * 1024) == 0:  # Every MB
            progress = (self.bytes_read / self.total_size) * 100
            print(f"Progress: {progress:.1f}% ({self.bytes_read / (1024*1024):.1f}MB/{self.total_size / (1024*1024):.1f}MB)")
        
        return chunk
    
    def seek(self, offset, whence=0):
        if self.file:
            return self.file.seek(offset, whence)
    
    def tell(self):
        if self.file:
            return self.file.tell()
        return 0

