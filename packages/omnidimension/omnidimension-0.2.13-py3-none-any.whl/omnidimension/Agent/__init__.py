
class Agent():
    def __init__(self, client):
        """
        Initialize the Agent client with a reference to the main API client.
        
        Args:
            client: The main API client instance.
        """
        self.client = client

    def list(self, page=1, page_size=30):
        """
        Get all agents for the authenticated user.
        
        Args:
            page (int): Page number for pagination (default: 1).
            page_size (int): Number of items per page (default: 30).
            
        Returns:
            dict: Response containing the list of agents.
        """
        params = {
            'pageno': page,
            'pagesize': page_size
        }
        return self.client.get("agents", params=params)
    
    def get(self, agent_id):
        """
        Get a specific agent by ID.
        
        Args:
            agent_id (int): The ID of the agent to retrieve.
            
        Returns:
            dict: Response containing the agent details.
        """
        return self.client.get(f"agents/{agent_id}")
    
    def create(self, name, context_breakdown, **kwargs):
        """
        Create a custom agent with the provided configuration and optional parameters.

        Args:
            name (str): name for the agent.
            context_breakdown (list): List of context breakdowns, each containing
                                      'title' and 'body'.
            **kwargs: Additional optional parameters to include in the API request.

        Returns:
            dict: Response from the API containing agent details.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Validate required inputs
        if not isinstance(name, str):
            raise ValueError("name must be a string.")
        if not isinstance(context_breakdown, list) or not all(
            isinstance(context, dict) and 'title' in context and 'body' in context
            for context in context_breakdown
        ):
            raise ValueError(
                "context_breakdown must be a list of dictionaries with 'title' and 'body'."
            )

        # Prepare the data payload
        data = {
            "name": name,
            "context_breakdown": context_breakdown,
            **kwargs  # Include any additional parameters
        }

        return self.client.post("agents/create", data=data)
    
    def update(self, agent_id, data):
        """
        Update an existing agent.
        
        Args:
            agent_id (int): The ID of the agent to update.
            data (dict): The updated agent data.
            
        Returns:
            dict: Response containing the updated agent details.
        """
        return self.client.put(f"agents/{agent_id}", data=data)
    
    def delete(self, agent_id):
        """
        Delete an agent.
        
        Args:
            agent_id (int): The ID of the agent to delete.
            
        Returns:
            dict: Response indicating success or failure.
        """
        return self.client.delete(f"agents/{agent_id}")
