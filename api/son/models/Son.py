from django.db import models
from api.operator.models import Operator

class Son(models.Model):
    id_son = models.AutoField(primary_key=True)
    operator = models.ForeignKey(
        Operator,
        on_delete=models.CASCADE,
        related_name='sons',
        db_column="id_operator"
    )
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.operator.id_operator} - Son"
