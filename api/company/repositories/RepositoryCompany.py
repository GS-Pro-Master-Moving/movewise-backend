from api.company.repositories.IRepositoryCompany import IRepositoryCompany
from api.company.models.Company import Company

class RepositoryCompany(IRepositoryCompany):
    def get_all(self):
        return Company.objects.all()

    def get_by_id(self, id: int):
        return Company.objects.get(id_company=id)

    def get_by_name(self, name: str):
        return Company.objects.filter(name=name).first()

    def create(self, company: Company) -> Company:
        company.save()  
        return company

    def update(self, company_instance: Company):
        return company_instance.save()

    def delete(self, id: int):
        company_instance = self.get_by_id(id)
        if company_instance:
            company_instance.delete()
            return True
        return False