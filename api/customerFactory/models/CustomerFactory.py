from django.db import models

class CustomerFactory(models.Model):
    id_factory = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    state = models.BooleanField(default=True,db_column='ACTIVE')
    def __str__(self):
        return self.name
