from api.plan.repositories.PlanRepository import PlanRepository

class PlanService:
    def list_plans(self):
        return PlanRepository.get_all()

    def get_plan(self, plan_id):
        return PlanRepository.get_by_id(plan_id)

    def create_plan(self, data):
        return PlanRepository.create(data)
