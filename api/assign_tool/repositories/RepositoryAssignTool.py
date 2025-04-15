
from api.assign_tool.models.AssignTool import AssignTool
from api.tool.models.Tool import Tool
from api.order.models.Order import Order
from api.assign_tool.repositories.IRepositoryAssignTool import IRepositoryAssignTool

class RepositoryAssignTool(IRepositoryAssignTool):
    def assign_tool(self, tool_id: str, order_id: str) -> bool:
        print("\nAssigning tool to order in repository")
        try:
            tool = Tool.objects.get(id=tool_id)
        except Tool.DoesNotExist:
            print("\nTool {tool_id} not found")
            return False
        try:
            order = Order.objects.get(key=order_id)
        except Order.DoesNotExist:
            print("\nOrder {order_id} not found")
            return False
        tool.order = order
        tool.save()
        AssignTool.objects.create(id_tool=tool, id_order=order, date=order.date)
        return True
    
    def unassign_tool(self, tool_id: int, order_id: str) -> bool:
        try:
            tool = Tool.objects.get(id=tool_id)
        except Tool.DoesNotExist:
            print("\nTool not found")
            return False
        try:
            order = Order.objects.get(key=order_id)
        except Order.DoesNotExist:
            print("\nOrder not found")
            return False
        assign_tool = assign_tool.objects.drop(tool=tool, order=order)
        if not assign_tool:
            print("\nAssignment not found")
            return False
        return True
    
    def get_assigned_tools(self, order_id: str) -> list:
        try:
            order = Order.objects.get(id_order=order_id)
        except Order.DoesNotExist:
            print("\nOrder not found")
            return []
        tools = Tool.objects.filter(order=order)
        return list(tools)
    
    def get_assigned_tools_by_job(self, job_id: int) -> list:
        try:
            order = Order.objects.get(id_order=job_id)
        except Order.DoesNotExist:
            print("\nOrder not found")
            return []
        tools = Tool.objects.filter(order=order)
        return list(tools)
    
    def create_assignments(self, data: list[dict]) -> list[dict]:
        results = []
        print("\nCreating ", data)
        for assign in data:
            tool_id = assign.get("id_tool")
            order_id = assign.get("id_order")
            print(tool_id, order_id)
            if not tool_id or not order_id:
                results.append({"tool_id": tool_id, "order_id": order_id, "status": "error", "message": "Invalid data"})
                continue
            
            success = self.assign_tool(tool_id, order_id)
            
            status = "success" if success else "error"
            message = "Assigned successfully" if success else "Assignment failed"
            results.append({"tool_id": tool_id, "order_id": order_id, "status": status, "message": message})

        return results