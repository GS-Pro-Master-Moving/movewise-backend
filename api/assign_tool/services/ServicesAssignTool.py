from api.assign_tool.services.IServicesAssignTool import IServicesAssignTool
from api.assign_tool.repositories.RepositoryAssignTool import RepositoryAssignTool
class ServicesAssignTool(IServicesAssignTool):
    
    def __init__(self, repository=None):
        self.repository = RepositoryAssignTool()
        
    def assign_tool(self, tool_id: int, order_id: str) -> bool:
        print("\nOrder {order_id} is being assigned to tool {tool_id}")
        return self.repository.assign_tool(tool_id, order_id)
    
    def unassign_tool(self, tool_id: int, order_id: str) -> bool:
        return self.repository.unassign_tool(tool_id, order_id)
    
    def get_assigned_tools(self, order_id: str) -> list:
        return self.repository.get_assigned_tools(order_id)