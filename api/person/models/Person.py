from django.db import models
from api.company.models.Company import Company

class Person(models.Model):
 
    id_person = models.AutoField(primary_key=True)
    #id_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    id_number = models.CharField(null=True, blank=True, unique=True, max_length=50)
    type_id = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column="id_company")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def pk(self):
        # DRF a veces usa .pk para identificar al user
        return self.id_person

    # Para que request.user.company_id funcione sin que tengas que volver
    # a leer el token en el middleware:
    @property
    def company_id(self):
        return self.id_company.id
 