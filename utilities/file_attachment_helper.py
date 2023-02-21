import requests
from urllib.parse import urljoin
import os
from dataclasses import dataclass


class FileAttachmentHelper:    
    def upload_file_to_s3(self, file_attachment: dict, file_object: bytes):
        """Upload file to s3 with signed URL."""
        with requests.put(
            url=file_attachment["uploadUrl"],
            headers={"Content-Type": file_attachment["fileAttachment"]["contentType"]},
            data=file_object,
        ) as response:
            response.raise_for_status()

    def download_file_attachment(self, url: str, file_name: str):
        # with open('/tmp/my-file', 'wb') as f:
        #     self.s3.download_fileobj(s3_bucket, file_path, f)
        response = requests.get(url)
        return response.content
        # with open('procedure_export/temp-files/' + file_name, 'wb') as f:
        #     f.write(response.content)

    def upload_file_attachment(self, file_object: bytes, file_name: str, file_attachment: dict):
        # with open(file_name, 'rb') as f:
        self.upload_file_to_s3(file_attachment, file_object)