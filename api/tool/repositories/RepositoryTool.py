from api.tool.models.Tool import Tool

class RepositoryTool:
    def get_all_tools(self):
        return Tool.objects.all()  
