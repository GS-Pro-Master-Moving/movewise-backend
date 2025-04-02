from abc import ABC, abstractmethod

class IServicesAssignTool(ABC):
    """
    Interface for the AssignTool service.
    
    This interface defines the standard operations for managing AssignTool entities.
    Implementations should provide the actual business logic and data interactions.
    """

    @abstractmethod
    def assign_tool(self, tool_id: int, order_id: str) -> bool:
        """
        Assigns a tool to a order.
        
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
            order_id (str): The ID of the person from whom the tool is unassigned.
        
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
            list: A list of tools assigned to the specified person.
        """
        pass