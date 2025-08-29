class KnowledgeBase():
    def __init__(self, client):
        """
        Initialize the KnowledgeBase client with a reference to the main API client.
        
        Args:
            client: The main API client instance.
        """
        self.client = client

    def list(self):
        """
        Get all knowledge base files for the authenticated user.
        
        Returns:
            dict: Response containing the list of files.
        """
        return self.client.get("knowledge_base/list")
    
    def create(self, file_data, filename):
        """
        Upload a file to the knowledge base.
        
        Args:
            file_data (str): Base64 encoded file content.
            filename (str): Name of the file (must end with .pdf).
            
        Returns:
            dict: Response containing the created file details.
            
        Raises:
            ValueError: If the file is not a PDF.
        """
        # Validate file is a PDF
        if not filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported.")
            
        data = {
            "file": file_data,
            "filename": filename
        }
        
        return self.client.post("knowledge_base/create", data=data)
    
    def can_upload(self, file_size, file_type="pdf"):
        """
        Validate if a file can be uploaded based on size and type.
        
        Args:
            file_size (int): Size of the file in bytes.
            file_type (str): Type of the file (only 'pdf' is supported).
            
        Returns:
            dict: Response containing validation result and quota information.
        """
        data = {
            "file_size": file_size,
            "file_type": file_type
        }
        
        return self.client.post("knowledge_base/can_upload", data=data)
    
    def delete(self, file_id):
        """
        Delete a file from the knowledge base.
        
        Args:
            file_id (int): ID of the file to delete.
            
        Returns:
            dict: Response indicating success or failure.
        """
        data = {
            "file_id": file_id
        }
        
        return self.client.post("knowledge_base/delete", data=data)
    
    def attach(self, file_ids, agent_id, when_to_use=None):
        """
        Attach multiple files to an agent.
        
        Args:
            file_ids (list): List of file IDs to attach.
            agent_id (int): ID of the agent to attach files to.
            when_to_use: when to use this files
            
        Returns:
            dict: Response indicating success or failure.
            
        Raises:
            ValueError: If file_ids is not a list or agent_id is not an integer.
        """
        if not isinstance(file_ids, list):
            raise ValueError("file_ids must be a list of integers.")
        if not isinstance(agent_id, int):
            raise ValueError("agent_id must be an integer.")
            
        data = {
            "file_ids": file_ids,
            "agent_id": agent_id,
            "when_to_use": when_to_use
        }
        
        return self.client.post("knowledge_base/attach", data=data)
    
    def detach(self, file_ids, agent_id):
        """
        Detach multiple files from an agent.
        
        Args:
            file_ids (list): List of file IDs to detach.
            agent_id (int): ID of the agent to detach files from.
            
        Returns:
            dict: Response indicating success or failure.
            
        Raises:
            ValueError: If file_ids is not a list or agent_id is not an integer.
        """
        if not isinstance(file_ids, list):
            raise ValueError("file_ids must be a list of integers.")
        if not isinstance(agent_id, int):
            raise ValueError("agent_id must be an integer.")
            
        data = {
            "file_ids": file_ids,
            "agent_id": agent_id
        }
        
        return self.client.post("knowledge_base/detach", data=data)