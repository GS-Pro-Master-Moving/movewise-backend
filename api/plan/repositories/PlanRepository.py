from plan.models.Plan import Plan

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
