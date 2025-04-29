from django.db import models
from api.plan.models.Plan import Plan

class Subscription(models.Model):
    id_subscription = models.AutoField(primary_key=True)
    #id_user = models.IntegerField()
    id_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, db_column='id_plan')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Subscription {self.id_subscription} "
