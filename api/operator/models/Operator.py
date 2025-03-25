from django.db import models
from api.order.models.Order import Order
from api.person.models.Person import Person
class Operator(models.Model):
    id_operator = models.AutoField(primary_key=True)
    
    #id_driver = models.IntegerField() by the moment not necesary
    number_licence = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    n_children = models.IntegerField(null=True, blank=True) 
    size_t_shift = models.CharField(max_length=20, null=True, blank=True)
    name_t_shift = models.CharField(max_length=100, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    photo = models.CharField(max_length=150, null=True, blank=True)  
    status = models.CharField(max_length=50, null=True, blank=True)
    
    # Relations
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='operator',db_column="id_person")
    assign = models.ManyToManyField(Order, through="Assign", related_name="assigned_operators",db_column="id_assign")

    def __str__(self):
        return f"Operator {self.id_operator} - {self.person.id_person if self.person else 'No Person Assigned'}"
