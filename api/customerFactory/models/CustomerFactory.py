from django.db import models

class CustomerFactory(models.Model):
    id_factory = models.IntegerField(editable=False)
    name = models.CharField(max_length=50, unique=True)