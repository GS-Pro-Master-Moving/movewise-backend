
from abc import ABC, abstractmethod

class IRepositoryAssignTool(ABC):
    def assign_tool(self, tool_id: int, order_id: str) -> bool:
        """
        Assigns a tool to an order.
        
        Args:
            tool_id (str): The ID of the tool to be assigned.
            order_id (str): The ID of the order to whom the tool is assigned.
        
        Returns:
            bool: True if the assignment was successful, False otherwise.
        """
        pass
    
    def unassign_tool(self, tool_id: int, order_id: str) -> bool:
        """
        Unassigns a tool from an order.
        
        Args:
            tool_id (str): The ID of the tool to be unassigned.
            order_id (str): The ID of the order from whom the tool is unassigned.
        
        Returns:
            bool: True if the unassignment was successful, False otherwise.
        """
        pass
    
    def get_assigned_tools(self, order_id: str) -> list:
        """
        Retrieves a list of tools assigned to an order.
        
        Args:
            order_id (str): The ID of the order whose assigned tools are to be retrieved.
        
        Returns:
            list: A list of tools assigned to the specified order.
        """
        pass
    
    def get_assigned_tools_by_job(self, job_id: int) -> list:
        """
        Retrieves a list of tools assigned to a job.
        
        Args:
            job_id (int): The ID of the job whose assigned tools are to be retrieved.
        
        Returns:
            list: A list of tools assigned to the specified job.
        """
        pass
    
    def create_assignments(self, data: list[dict]) -> list[dict]:
        """
        Creates multiples assignaments
        """
        pass
    
    