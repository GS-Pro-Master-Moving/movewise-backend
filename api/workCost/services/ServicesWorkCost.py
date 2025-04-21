from typing import List
from api.workCost.models.WorkCost import WorkCost
from api.workCost.repositories.RepositoryWorkCost import RepositoryWorkCost
from api.workCost.services.IServicesWorkCost import IServicesWorkCost


class ServicesWorkCost(IServicesWorkCost):
    def __init__(self):
        self.repository = RepositoryWorkCost()
        
    def get_workCost_by_KeyOrder(self, KeyOrder) -> List[WorkCost]:
        return self.repository.get_workCost_by_KeyOrder(KeyOrder)
