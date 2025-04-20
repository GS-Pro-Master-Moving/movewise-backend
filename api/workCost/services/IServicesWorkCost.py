from abc import ABC, abstractmethod
from typing import List
from api.workCost.models.WorkCost import WorkCost
class IServicesWorkCost(ABC):

    @abstractmethod
    def get_workCost_by_KeyOrder(self, KeyOrder) -> List[WorkCost]:
        """Returns a list of work cost."""
        pass
