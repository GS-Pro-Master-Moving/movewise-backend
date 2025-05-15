from django.forms import ValidationError
from api.tool.repositories.RepositoryTool import RepositoryTool
from api.tool.models.Tool import Tool
from api.tool.serializers.SerializerTool import ToolSerializer
class ServicesTool:
    def __init__(self):
        self.repository = RepositoryTool() 

    def get_all_tools(self, company_id):
        # Filter tools whose work belongs to the company and state is True
        return Tool.objects.filter(
            company_id=company_id,
            state=True
        ).all()
    
    def create_tool(self, data, company_id):
        """
        Create a new tool associated with a company.
        """
        # Obtener la instancia de la compañía
        from api.company.models.Company import Company

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise ValidationError({"company": "Company not found."})

        # Validar y crear la herramienta
        serializer = ToolSerializer(data=data)
        if serializer.is_valid():
            return serializer.save(company=company)  # Pasar la compañía explícitamente
        else:
            raise ValidationError(serializer.errors)