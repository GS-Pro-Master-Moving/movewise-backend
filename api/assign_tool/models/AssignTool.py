from django.db import models
from api.tool.models.Tool import Tool
from api.order.models.Order import Order

class AssignTool(models.Model):
    id_tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="assign_tool", db_column="id_tool")
    key = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="assign_tool", db_column="key")
    id_assign_tool = models.AutoField(primary_key=True, db_column="id_assign_tool")
    date = models.DateField(null=True, blank=True)  # Order date