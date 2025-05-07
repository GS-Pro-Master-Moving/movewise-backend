from typing import List
from api.workCost.models.WorkCost import WorkCost
from api.workCost.repositories.IRepositoryWorkCost import IRepositoryWorkCost
class RepositoryWorkCost(IRepositoryWorkCost):

    def get_workCost_by_KeyOrder(self, KeyOrder) -> List[WorkCost]:
        """Returns a list of work cost."""
        result = WorkCost.objects.filter(id_order=KeyOrder)
        print("Result get_workCost_by_KeyOrder: ", result)
        return result