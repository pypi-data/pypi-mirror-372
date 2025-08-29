import os
import requests
from heaptree.enums import NodeSize, NodeType, OperatingSystem
from heaptree.exceptions import HeaptreeAPIException
from heaptree.response_wrappers import CreateNodeResponseWrapper


class Heaptree:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://8s22jeo8qb.execute-api.us-east-1.amazonaws.com/prod"
        #self.base_url = "http://0.0.0.0:8000"

    def call_api(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.api_key}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise HeaptreeAPIException(f"Error {response.status_code}: {response.text}")
        return response.json()

    def create_node(
        self,
        os: OperatingSystem = OperatingSystem.LINUX,
        num_nodes: int = 1,
        node_type: NodeType = NodeType.UBUNTU,
        node_size: NodeSize = NodeSize.SMALL,
        lifetime_seconds: int = 330,# 5 minutes
        applications: list[str] = [],
    ) -> CreateNodeResponseWrapper:
        """
        Create one or more nodes.
        
        Returns CreateNodeResponseWrapper with convenient access:
        - result.node_id (for single node)
        - result.node_ids (for multiple nodes)
        - result.web_access_url (for single node)
        - result.web_access_urls (for multiple nodes)
        """
        data = {
            "os": os.value,
            "num_nodes": num_nodes,
            "node_size": node_size.value,
            "node_type": node_type.value,
            "lifetime_seconds": lifetime_seconds,
            "applications": applications,
        }
        raw_response = self.call_api("/create-node", data)
        return CreateNodeResponseWrapper(raw_response)

    def terminate_node(self, node_id: str):
        data = {
            "node_id": node_id,
        }
        return self.call_api("/cleanup-node", data)

    def upload(
    self,
    node_id: str,
    file_path: str,
    destination_path: str = None
):
        """
        Upload a file to a node and transfer it to the node's filesystem.
        
        Args:
            node_id: The ID of the node to upload to
            file_path: Local path to the file to upload
            destination_path: Optional path on the node where file should be placed
                            (defaults to /home/ubuntu/Desktop/YOUR_FILES/)
        
        Returns:
            dict: Response containing upload status and transfer details
        """
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract filename from path
        filename = os.path.basename(file_path)
        
        # Step 1: Get presigned upload URL
        upload_url_data = {
            "node_id": node_id,
            "filename": filename
        }
        
        upload_response = self.call_api("/get-upload-url", upload_url_data)
        if not upload_response:
            raise Exception(f"Failed to get upload URL: {upload_response}")
        print(upload_response)
        
        # Step 2: Upload file to S3 using presigned URL
        upload_url = upload_response["upload_url"]
        fields = upload_response["fields"]
        
        try:
            with open(file_path, 'rb') as file:
                # Prepare multipart form data
                files = {'file': (filename, file, 'application/octet-stream')}
                
                # Upload to S3
                s3_response = requests.post(upload_url, data=fields, files=files)
                s3_response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
        
        # Step 3: Transfer file from S3 to node filesystem
        transfer_data = {
            "node_id": node_id
        }
        
        transfer_response = self.call_api("/transfer-files", transfer_data)
        
        return {
            "upload_status": "success",
            "filename": filename,
            "s3_upload": "completed",
            "transfer_response": transfer_response
        }

    def download(
        self, node_id: str, remote_path: str, local_path: str
    ):
        data = {
            "node_id": node_id,
            "file_path": remote_path,  # API still expects 'file_path'
        }
        response_json = self.call_api("/download-files", data)
        s3_url = response_json.get("download_url")

        if not s3_url:
            return {"error": "No download URL found."}

        try:
            download_response = requests.get(s3_url)
            download_response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(download_response.content)
            return {"status": "success", "file_path": local_path}
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to download file: {e}"}

    def run_command(self, node_id: str, command: str):
        data = {"node_id": node_id, "command": command}
        return self.call_api("/run-command", data)
