from django.db import models
from api.person.models import Person  # Cambia esta importación

class Operator(models.Model):  # No heredes de Person
    id_operator = models.AutoField(primary_key=True)
    person = models.OneToOneField(
        Person, 
        on_delete=models.CASCADE, 
        related_name='operator',
        db_column="id_person"
    )
    number_licence = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    n_children = models.IntegerField(null=True, blank=True) 
    size_t_shift = models.CharField(max_length=20, null=True, blank=True)
    name_t_shift = models.CharField(max_length=100, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    photo = models.CharField(max_length=150, null=True, blank=True)  
    status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Operator {self.id_operator} - {self.person.id_number if self.person else 'No Person Assigned'}"

    class DoesNotExist(Exception):
        pass
