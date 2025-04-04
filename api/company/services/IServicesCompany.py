from abc import ABC, abstractmethod
class IServicesCompany(ABC):
    @abstractmethod
    def get_all_companies(self):
        pass

    @abstractmethod
    def get_company_by_id(self, id: int):
        pass
    
    @abstractmethod
    def get_company_by_name(self, name: str):
        pass

    @abstractmethod
    def create_company(self, company: dict):
        pass

    @abstractmethod
    def update_company(self, id: int, company: dict):
        pass

    @abstractmethod
    def delete_company(self, id: int):
        pass