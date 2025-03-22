from api.tool.repositories.RepositoryTool import RepositoryTool

class ServicesTool:
    def __init__(self):
        self.repository = RepositoryTool() 

    def get_all_tools(self):
        return self.repository.get_all_tools()  
