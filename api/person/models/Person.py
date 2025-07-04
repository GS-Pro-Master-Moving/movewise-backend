from django.db import models
from django.db.models.query import QuerySet
from api.company.models.Company import Company

class PersonQuerySet(QuerySet):
    def active(self):
        """Filtrar solo personas activas."""
        return self.filter(status='active')

class PersonManager(models.Manager):
    def get_queryset(self):
        """Retorna un QuerySet personalizado."""
        return PersonQuerySet(self.model, using=self._db)
    
    def active(self):
        """Retorna solo personas activas."""
        return self.get_queryset().active()

class Person(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
 
    id_person = models.AutoField(primary_key=True)
    #id_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=100,null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    id_number = models.CharField(null=True, blank=True, max_length=50)
    type_id = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=False, null=True, blank=True)
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column="id_company")
    #new status
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,null=True,blank=True,default='active')

    objects = PersonManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def soft_delete(self):
        """set inactive person"""
        self.status = 'inactive'
        self.save()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return False

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def pk(self):
        # DRF a veces usa .pk para identificar al user
        return self.id_person

    # Para que request.user.company_id funcione sin que tengas que volver
    # a leer el token en el middleware:
    @property
    def company_id(self):
        return self.id_company.id
 