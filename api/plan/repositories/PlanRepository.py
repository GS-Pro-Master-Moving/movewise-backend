from api.plan.models.Plan import Plan

class PlanRepository:
    @staticmethod
    def get_all():
        return Plan.objects.all()

    @staticmethod
    def get_by_id(plan_id):
        return Plan.objects.filter(id_plan=plan_id).first()

    @staticmethod
    def create(data):
        return Plan.objects.create(**data)
    
    @staticmethod
    def delete(plan_id):
        plan = PlanRepository.get_by_id(plan_id)
        if plan:
            plan.delete()
            return True
        return False
    
    @staticmethod
    def update_partial(plan_id, data):
        plan = PlanRepository.get_by_id(plan_id)
        if plan:
            for attr, value in data.items():
                setattr(plan, attr, value)
            plan.save()
            return plan
        return None