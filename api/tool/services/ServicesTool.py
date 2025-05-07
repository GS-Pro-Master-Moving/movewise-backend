from api.tool.repositories.RepositoryTool import RepositoryTool
from api.tool.models.Tool import Tool
class ServicesTool:
    def __init__(self):
        self.repository = RepositoryTool() 

    def get_all_tools(self, company_id):
        # Filter tools whose work belongs to the company
        return Tool.objects.filter(job__id_company=company_id).select_related('job')
