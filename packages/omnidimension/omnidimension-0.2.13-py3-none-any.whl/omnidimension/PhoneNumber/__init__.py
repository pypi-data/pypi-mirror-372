class PhoneNumber():
    def __init__(self, client):
        """
        Initialize the PhoneNumber client with a reference to the main API client.
        
        Args:
            client: The main API client instance.
        """
        self.client = client

    def list(self, page=1, page_size=30):
        """
        Get all phone numbers for the authenticated user.
        
        Args:
            page (int): Page number for pagination (default: 1).
            page_size (int): Number of items per page (default: 30).
            
        Returns:
            dict: Response containing the list of phone numbers.
        """
        params = {
            'pageno': page,
            'pagesize': page_size
        }
        return self.client.get("phone_number/list", params=params)
    
    def attach(self, phone_number_id, agent_id):
        """
        Attach a phone number to an agent.
        
        Args:
            phone_number_id (int): ID of the phone number to attach.
            agent_id (int): ID of the agent to attach the phone number to.
            
        Returns:
            dict: Response indicating success or failure.
            
        Raises:
            ValueError: If phone_number_id or agent_id is not an integer.
        """
        if not isinstance(phone_number_id, int):
            raise ValueError("phone_number_id must be an integer.")
        if not isinstance(agent_id, int):
            raise ValueError("agent_id must be an integer.")
            
        data = {
            "phone_number_id": phone_number_id,
            "agent_id": agent_id
        }
        
        return self.client.post("phone_number/attach", data=data)
    
    def detach(self, phone_number_id):
        """
        Detach a phone number from any agent it's attached to.
        
        Args:
            phone_number_id (int): ID of the phone number to detach.
            
        Returns:
            dict: Response indicating success or failure.
            
        Raises:
            ValueError: If phone_number_id is not an integer.
        """
        if not isinstance(phone_number_id, int):
            raise ValueError("phone_number_id must be an integer.")
            
        data = {
            "phone_number_id": phone_number_id
        }
        
        return self.client.post("phone_number/detach", data=data)