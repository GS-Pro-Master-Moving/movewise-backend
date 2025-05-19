from api.tool.models.Tool import Tool

class RepositoryTool:
    def get_all_tools(self):
        return Tool.objects.filter(state=True).all()  

    def get_job_tools(self, company_id, id_job):
        return Tool.objects.filter(
            company_id=company_id,
            job_id=id_job,
            state=True
        ).order_by('id')#Ordered by id