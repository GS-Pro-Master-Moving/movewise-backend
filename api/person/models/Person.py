from django.db import models

class Person(models.Model):
    id_person = models.AutoField(primary_key=True)
    #id_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    id_number = models.BigIntegerField(null=True, blank=True)
    type_id = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
