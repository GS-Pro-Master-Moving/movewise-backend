from api.company.models.Company import Company
from api.company.repositories.RepositoryCompany import RepositoryCompany
from api.company.services.IServicesCompany import IServicesCompany

class ServicesCompany(IServicesCompany):
    """
    Services for managing Company entities.

    Provides methods for:
    - Creating a company.
    - Updating a company.
    - Deleting a company.
    - Retrieving all companies.
    - Retrieving a company by ID.
    - Retrieving a company by name.
    """

    def __init__(self):
        self.repository = RepositoryCompany()  
        
    def get_all_companies(self):
        return self.repository.get_all()
    
    def get_company_by_id(self, id: int):
        return self.repository.get_by_id(id)
    
    def get_company_by_name(self, name: str):
        return self.repository.get_by_name(name)
    
    def create(self, company_data: dict) -> Company:
        company = Company(**company_data)  # convets dict to Company instance
        return self.repository.create(company)
    
    def update_company(self, id: int):
        # lookup the existing company instance
        company_instance = self.repository.get_by_id(id)
        if not company_instance:
            raise ValueError("Company not found")
        return self.repository.update(company_instance)
    
    def delete_company(self, id):
        return self.repository.delete(id)