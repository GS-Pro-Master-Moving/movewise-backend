from api.company.repositories.IRepositoryCompany import IRepositoryCompany
from api.company.models.company import company

class RepositoryCompany(IRepositoryCompany):
    def get_all(self):
        return company.objects.all()

    def get_by_id(self, id: int):
        return company.objects.get(id_company=id)

    def get_by_name(self, name: str):
        return company.objects.filter(name=name).first()

    def create(self, company_instance: company):
        return company_instance.save()

    def update(self, company_instance: company):
        return company_instance.save()

    def delete(self, id: int):
        company_instance = self.get_by_id(id)
        if company_instance:
            company_instance.delete()
            return True
        return False